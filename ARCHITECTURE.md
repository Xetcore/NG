# PilotNG Architectural Overview

## Introduction

This document outlines the software architecture, implemented features, and potential future enhancements for the PilotNG application, a game assistance bot designed to automate tasks in a specific game.

## Core Architecture

### Key Technologies & Principles
*   Python 3.11
*   CustomTkinter for UI
*   Poetry for dependency management and packaging
*   PyInstaller for executable creation
*   Modular design: Separation of concerns into distinct layers (UI, Gameplay Logic, Game Interaction Repositories, Utilities).
*   Stateful task-based automation: Core actions are broken down into individual, manageable tasks orchestrated by a central system.
*   Screen scraping and image recognition: Utilizes libraries like OpenCV, MSS, and DXCam for real-time game state detection from screen captures.
*   Simulated Input: Uses PyAutoGUI for keyboard/mouse simulation, with considerations for Arduino-based input for enhanced reliability/stealth.
*   External JSON Configuration: Application behavior, hotkeys, and certain game-specific data are configurable via JSON files, promoting flexibility.
*   Event-driven (UI) and polling-based (gameplay loop) interactions.

### Main Architectural Layers

1.  **Presentation Layer (UI - `src/ui/`)**
    *   **Responsibilities**: Handles all user interactions, displays game and bot status information, provides controls for starting/stopping the bot, and allows configuration of settings and scripts.
    *   **Technologies**: Built primarily with `customtkinter`.
    *   **Key Components**:
        *   `application.py`: Main application window and Potion/Healing/Cavebot/Combo/Inventory/Configuration pages.
        *   `pages/`: Contains modules for different UI views like the main settings page (`settings_page.py`), cavebot script editor (`cavebotPage.py`), healing configuration, etc.
        *   Dialogs and modals for specific interactions (e.g., waypoint options).

2.  **Gameplay Logic Layer (`src/gameplay/`)**
    *   **Responsibilities**: Contains the core intelligence and decision-making of the bot. It manages the overall state and orchestrates actions based on user settings and game events.
    *   **Key Components**:
        *   `context.py`: A central dictionary holding the runtime state of the bot (e.g., player status, cavebot waypoints, targeting information, loaded spell sequences).
        *   `cavebot.py`: Manages the execution flow of cavebot scripts, deciding when to fetch new tasks based on the current state.
        *   `core/tasks/`: Defines individual, atomic actions the bot can perform (e.g., `MoveTask`, `AttackClosestCreatureTask`, `LootCorpseTask`, `ExecuteSpellSequenceTask`). Each task is typically a class inheriting from `BaseTask`.
        *   `core/tasks/orchestrator.py` (`TasksOrchestrator`): Manages the lifecycle of tasks (starting, running, completing, handling delays, and interruptions).
        *   `healing/`: Logic for automated health and mana management.
        *   `spells.py`: Contains definitions for known game spells (`KNOWN_SPELLS`) and TypedDicts for `SpellAction`, `SpellDefinition`, and `SpellSequence`.
        *   `typings.py`: Defines shared `TypedDict` structures and type aliases used within the gameplay layer, including `SpellSequence`.

3.  **Game Interaction Layer (Repositories - `src/repositories/`)**
    *   **Responsibilities**: Abstracts direct interaction with the game client. This layer is responsible for "seeing" the game state and "acting" within the game.
    *   **Key Components**:
        *   Modules for specific game UI elements or information panels: `actionBar`, `battleList`, `gameWindow`, `radar`, `statsBar`, `statusBar`, `inventory`, `chat`.
        *   Each module typically contains:
            *   `core.py`: Main logic for reading information or performing actions related to that game element.
            *   `extractors.py`: Functions to get specific data from images (e.g., health/mana values, item counts).
            *   `locators.py`: Predefined coordinates or methods to find elements on screen.
            *   `images/`: Template images used for recognition.
            *   `config.py`: Configuration specific to the repository, like image paths.

4.  **Utilities Layer (`src/utils/`)**
    *   **Responsibilities**: Provides common, reusable helper functions and classes that are used across different layers of the application.
    *   **Key Components**:
        *   `keyboard.py`, `mouse.py`: Low-level keyboard and mouse input simulation (currently using PyAutoGUI, with Arduino as a suggested alternative).
        *   `image.py`, `screen_capture.py`: Image processing utilities (e.g., loading, converting, finding sub-images) and screen grabbing functionalities.
        *   `coordinate.py`: Helper functions for manipulating game coordinates.
        *   `config_manager.py`: Handles loading and saving of application settings from JSON files (`config.json`, `config.default.json`).
        *   `script_parser.py`: Validates the syntax and structure of `.pilotscript` files.

5.  **Data and Configuration (Root & `src/wiki/`)**
    *   **Responsibilities**: Manages persistent data, user configurations, and potentially static game knowledge.
    *   **Key Components**:
        *   `config.json` (in root, user-generated): Stores user-specific application settings.
        *   `config.default.json` (in root): Provides a template and default values for all configurable settings.
        *   `.pilotscript` files (typically in `scripts/`): User-created JSON files defining cavebot waypoint sequences.
        *   `src/wiki/`: Currently contains Python files defining lists of game items like cities, creatures, spells. This could be expanded or replaced by more dynamic data loading.
        *   `file.json` (in root, user-generated): Stores UI-specific profile data, like selected cavebot script path, backpack choices, etc. (Managed by `src/ui/context.py`).

### Application Flow Overview
1.  **Initialization**:
    *   The main application (`src/ui/application.py`) starts.
    *   `src/utils/config_manager.py` loads application settings from `config.json`, `config.default.json`, or internal defaults.
    *   The main UI window is created, providing buttons to access different features (Cavebot, Healing, Settings, etc.).
    *   The initial gameplay context (`src/gameplay/context.py`) is established, potentially overridden by loaded settings.

2.  **User Interaction & Configuration**:
    *   The user interacts with the UI to:
        *   Load a `.pilotscript` file via the Cavebot page. The script is parsed and validated by `script_parser.py`. `defineSpellSequence` waypoints are processed and stored in `context['ng_spellSequences']`, while executable waypoints are loaded into `context['ng_cave']['waypoints']['items']`.
        *   Adjust settings via the Settings Page. These changes can be saved back to `config.json`.
        *   Configure healing rules, targeting, etc.

3.  **Bot Operation (Cavebot Example)**:
    *   User enables the Cavebot.
    *   The main gameplay loop (implicitly managed through `src/gameplay/cavebot.py` and the `TasksOrchestrator`) begins.
    *   `shouldAskForCavebotTasks` (in `cavebot.py`) determines if a new cavebot task should be fetched. This typically happens if no task is running or the current task has finished, and no higher-priority actions (like combat) are pending.
    *   If a new task is needed, `resolveCavebotTasks` (in `cavebot.py`):
        *   Retrieves the current waypoint from `context['ng_cave']['waypoints']['items']`.
        *   Calls `get_task_from_waypoint` to map the waypoint data to a specific `BaseTask` derivative (e.g., `MoveTask`, `RefillTask`, `ExecuteSpellSequenceTask`).
        *   Sets this new task as the `rootTask` in the `TasksOrchestrator` using `setRootTask()`.
    *   The `TasksOrchestrator.do()` method is called repeatedly (likely driven by the main application's update cycle or a dedicated thread):
        *   It navigates the current task tree (if tasks are nested, like `VectorTask`).
        *   It handles task lifecycle: `onBeforeStart`, `do` (or `ping` for ongoing tasks), `onComplete`, delays, retries, and interruptions.
        *   Individual tasks (e.g., `ExecuteSpellSequenceTask`) implement their specific logic in their `do()` method. This often involves:
            *   Reading from the game state via Repositories (`src/repositories/`).
            *   Performing actions via Utilities (`src/utils/keyboard.py`, `mouse.py`).
            *   Updating the shared `context`.
    *   The main loop also handles priority overrides, like initiating combat tasks (`AttackClosestCreatureTask`) if enemies are detected, potentially interrupting the current cavebot task.

4.  **State Updates & UI Refresh**:
    *   The UI periodically refreshes or observes changes in the `context` to display up-to-date information (e.g., player health, current task, loot messages).

## Implemented Features

1.  **Executable Packaging**
    *   **Purpose**: To allow users to run PilotNG as a standalone application on Windows (and potentially Linux) without needing to install Python or manage dependencies manually.
    *   **Implementation**: Utilizes PyInstaller, configured via `pilotng.spec`. This spec file bundles the main script (`main.py`), all necessary source code, assets (images, .npy files from repositories), and the `config.default.json` file into a distributable package. The `run_pilotng.sh` and `run_pilotng.bat` scripts include an option to trigger the PyInstaller build process.
    *   **Key Files/Modules**: `pilotng.spec`, `run_pilotng.sh`, `run_pilotng.bat`, PyInstaller tool.
    *   **Outcome**: Produces an executable (`pilotng.exe` or `pilotng`) in the `dist` folder, simplifying distribution and setup for end-users.

2.  **External JSON Configuration**
    *   **Purpose**: To externalize application settings, allowing users to customize behavior without modifying the source code and to persist these settings across sessions.
    *   **Implementation**: A `ConfigManager` (`src/utils/config_manager.py`) handles loading and saving settings. It follows a priority:
        1.  `config.json`: User-specific configurations.
        2.  `config.default.json`: Shipped with the application, provides default values and a template.
        3.  In-memory defaults: Hardcoded defaults within `config_manager.py` as a final fallback.
        The manager supports nested configuration structures and provides `get_config()` for accessing values and `save_config()` for persisting them.
    *   **Key Files/Modules**: `src/utils/config_manager.py`, `config.default.json` (created in root), `config.json` (user-generated in root).
    *   **Outcome**: Flexible and persistent application settings for hotkeys, delays, paths, UI preferences, and game-specific parameters.

3.  **UI for Configuration Management**
    *   **Purpose**: To provide a graphical interface for users to easily view and modify the settings managed by the `ConfigManager`.
    *   **Implementation**: A dedicated `SettingsPage` (`src/ui/pages/settings_page.py`) was created using CustomTkinter. It features:
        *   A sidebar for navigating different setting categories (General, Items & Names, Gameplay & Combat, Hotkeys, etc.).
        *   Dynamic content areas for each category, populated with appropriate input widgets (entries, checkboxes, comboboxes, list editors for backpacks).
        *   Widgets are pre-filled with current values from `config_manager.get_config()`.
        *   "Save Settings" button: Collects values from all UI widgets, performs basic validation/type conversion, and uses `config_manager.save_config()` to write to `config.json`. Informs the user about potential restart needs.
        *   "Reset to Defaults" button: Repopulates UI widgets with values from `config_manager.get_initial_defaults()`, prompting the user to save if they wish to persist these defaults.
    *   **Key Files/Modules**: `src/ui/pages/settings_page.py`, `src/utils/config_manager.py`, `src/ui/application.py` (for launching the page).
    *   **Outcome**: Users can manage application settings through an intuitive GUI, reducing the need for manual JSON editing.

4.  **Cavebot Script Validation**
    *   **Purpose**: To help users identify structural and logical errors in their `.pilotscript` files before execution, improving script reliability.
    *   **Implementation**: A `ScriptParser` (`src/utils/script_parser.py`) was developed. It:
        *   Validates overall JSON structure.
        *   Checks each waypoint for required keys (`label`, `type`, `coordinate`, `options`, `ignore`, `passinho`) and their basic data types.
        *   Verifies waypoint `type` against a list of `KNOWN_WAYPOINT_TYPES`.
        *   Performs detailed validation of the `options` object for each waypoint type, including required keys, data types, and value constraints (e.g., valid directions, known city/item names from predefined lists).
        *   Cross-references labels for `refillChecker.waypointLabelToRedirect` and `executeSpellSequence.sequenceLabel` to ensure they point to defined labels/sequences within the script.
        *   Checks for duplicate waypoint labels and duplicate `defineSpellSequence` labels.
        This functionality is integrated into the Cavebot UI (`src/ui/pages/cavebot/cavebotPage.py`) via a "Validate Script" button, which displays errors in a messagebox. Scripts are also validated upon loading.
    *   **Key Files/Modules**: `src/utils/script_parser.py`, `src/ui/pages/cavebot/cavebotPage.py`, `src/gameplay/spells.py` (for `KNOWN_SPELLS`).
    *   **Outcome**: Users get immediate feedback on script errors, facilitating easier debugging and more robust script creation.

5.  **Spell Sequence Library for Cavebot**
    *   **Purpose**: To enable users to define reusable sequences of spell casts (e.g., combat combos, buff routines) and execute them as single actions within their cavebot scripts, making scripts more powerful and readable.
    *   **Implementation**:
        *   **Definitions (`src/gameplay/spells.py`)**: Introduced `SpellAction`, `SpellDefinition`, and `SpellSequence` TypedDicts. `KNOWN_SPELLS` dictionary stores definitions of game spells.
        *   **Scripting**: Added two new waypoint types:
            *   `defineSpellSequence`: Allows users to define a named sequence of `SpellAction`s within their script. Its `options` include `sequenceLabel` and a list of `spells` (actions).
            *   `executeSpellSequence`: Executes a pre-defined spell sequence by its `sequenceLabel`.
        *   **Parsing & Validation (`src/utils/script_parser.py`)**: The script parser was extended to validate the structure and content of these new waypoint types, including checking spell names against `KNOWN_SPELLS` and ensuring `executeSpellSequence` refers to a defined label.
        *   **Context Storage (`src/gameplay/context.py`)**: A new key `ng_spellSequences` (dictionary) was added to the main application context to store loaded spell sequence definitions.
        *   **Script Loading (`src/ui/pages/cavebot/cavebotPage.py`)**: The `loadScript` method now processes `defineSpellSequence` waypoints, populating `ng_spellSequences`. These definition waypoints are then filtered out from the list of waypoints passed to the task orchestrator.
        *   **Execution Task (`src/gameplay/core/tasks/executeSpellSequenceTask.py`)**: A new `ExecuteSpellSequenceTask` was created. It retrieves a sequence by its label from the context and executes its spell actions one by one, respecting defined delays and basic targeting. It's a stateful task that manages its own progress through the sequence.
        *   **Orchestrator Integration (`src/gameplay/cavebot.py`)**: The cavebot logic now includes a `get_task_from_waypoint` helper that instantiates `ExecuteSpellSequenceTask` when an `executeSpellSequence` waypoint is encountered.
    *   **Key Files/Modules**: `src/gameplay/spells.py`, `src/utils/script_parser.py`, `src/gameplay/context.py`, `src/ui/pages/cavebot/cavebotPage.py`, `src/gameplay/core/tasks/executeSpellSequenceTask.py`, `src/gameplay/cavebot.py`.
    *   **Outcome**: Cavebot scripts can now define and use complex, reusable spell sequences, significantly enhancing automation capabilities for combat and support actions.


## Potential Next Steps/Future Enhancements

1.  **Scripting Engine Enhancements**
    *   **Real-time Script Validation**: Provide validation feedback in the Cavebot UI as the user types or modifies the script, rather than only on button click or load.
    *   **"Library of Labels"**: Allow users to define a global library of common coordinates or important spots with labels (e.g., "DepotEntrance", "ManaShopNPC") that can be referenced by name in scripts.
    *   **Conditional Waypoints**: Introduce `if/else` logic (e.g., `if player_hp_percent < 30 then execute_sequence('PanicHeal') else continue()`). This would require a more advanced script execution model.
    *   **Looping/Goto Waypoints**: Allow `gotoLabel` type waypoints or loop constructs for more complex pathing or repeating actions not covered by `refillChecker`.
    *   **Variable Support**: Allow scripts to define, modify, and use simple variables (e.g., counters, flags) to enable more dynamic behavior.
    *   **Improved Error Reporting**: For script validation errors, provide more context, like line numbers or a way to highlight the problematic waypoint in the UI.

2.  **Spell System Improvements**
    *   **Advanced Spell Targeting**: Implement more sophisticated `target_type` options for `SpellAction` (e.g., "target_random_monster_in_range", "target_lowest_hp_monster", "target_creature_by_name_pattern", "target_next_creature_in_battlelist"). This would require deeper integration with battle list analysis and game state.
    *   **Cooldown Management**: Store cooldowns in `KNOWN_SPELLS` and have `ExecuteSpellSequenceTask` (or a global spell manager) respect them, preventing spamming and ensuring spells are ready.
    *   **Buff Monitoring & Recasting**: Add tasks or logic to monitor active buffs (e.g., "Haste", "Utura Gran") and automatically recast them when they expire or under certain conditions.
    *   **Dynamic Mana Cost**: Load actual mana costs from `KNOWN_SPELLS` into `SpellAction` if not overridden by the user. The system could then check if the player has enough mana before attempting a cast.
    *   **Spell Failure Detection**: Attempt to detect if a spell cast failed (e.g., "not enough mana", "target out of range" messages in game chat) and react accordingly (e.g., retry, log error).

3.  **User Interface & User Experience**
    *   **Refined Hotkey Configuration**: Allow direct key capture for hotkey settings in the UI instead of manual string input.
    *   **Visual Script Editor**: A graphical interface for creating/editing cavebot scripts by placing waypoints on a visual map representation of the game world.
    *   **Log Viewer**: An in-app log viewer with filtering capabilities for easier debugging and monitoring of bot actions.
    *   **Status Bar Enhancements**: More detailed real-time status information in the main UI (current task, target, next action, etc.).
    *   **Internationalization (i18n)**: Add support for multiple languages in the UI and for game-specific keywords (NPC dialog, item names if not solely image-based).
    *   **Profile Management**: More robust management of different character profiles/configurations within the UI.

4.  **Core Functionality & Robustness**
    *   **Comprehensive Error Handling**: Implement more specific error handling and recovery mechanisms throughout the application, especially in task execution and game interaction layers.
    *   **State Management Refinement**: Potentially move towards a more formally defined state machine for player actions and overall bot context to handle complex state transitions more reliably.
    *   **Resource Management**: Ensure efficient use of system resources, particularly for continuous screen capture and image processing, to minimize performance impact.
    *   **Cross-platform Input**: Finalize and test Arduino-based input as a more robust alternative to PyAutoGUI for different game clients or anti-cheat environments.
    *   **Dependency Management for Game Updates**: Design a system to more easily update image templates or game element locators when the game client receives updates that change UI or graphics.

5.  **Testing & Maintainability**
    *   **Unit Test Coverage**: Significantly increase unit test coverage for core logic (tasks, context manipulation, utilities like `config_manager` and `script_parser`).
    *   **Integration Tests**: Develop integration tests for key gameplay loops (e.g., completing a simple cavebot script with refill, executing a spell sequence).
    *   **Code Documentation**: Add more detailed docstrings, comments, and potentially update this `ARCHITECTURE.md` as the system evolves.
    *   **Refactor Large Files**: Break down very large files (if any emerge) into smaller, more focused modules.
```
