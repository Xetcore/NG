from src.gameplay.core.tasks.clickInClosestCreature import ClickInClosestCreatureTask


def test_should_test_default_params():
    task = ClickInClosestCreatureTask()
    assert task.name == 'clickInClosestCreature'
    assert task.delayOfTimeout == 1

def test_should_method_shouldIgnore_return_False_when_has_no_target_creature():
    context = {'ng_cave': {'targetCreature': None}}
    task = ClickInClosestCreatureTask()
    assert task.shouldIgnore(context) == False

def test_should_method_shouldIgnore_return_True_when_has_target_creature():
    context = {'ng_cave': {'targetCreature': ('Dragon', 'monster', True, (0, 0), (0, 0, 0), (0, 0), (0, 0), False)}}
    task = ClickInClosestCreatureTask()
    assert task.shouldIgnore(context) == True

def test_should_method_did_return_False_when_is_not_attacking_some_creature():
    context = {'ng_cave': {'isAttackingSomeCreature': False}}
    task = ClickInClosestCreatureTask()
    assert task.did(context) == False

def test_should_method_did_return_True_when_is_attacking_some_creature():
    context = {'ng_cave': {'isAttackingSomeCreature': True}}
    task = ClickInClosestCreatureTask()
    assert task.did(context) == True

def test_should_do_and_ignore_hotkey_attack_when_there_are_players(mocker):
    context = {
        'ng_cave': {'closestCreature': {'windowCoordinate': (0, 0)}},
        'gameWindow': {'players': [('Bubble', 'player', True, (0, 0), (0, 0, 0), (0, 0), (0, 0), False)]}
    }
    keyDownSpy = mocker.patch('src.utils.keyboard.keyDown')
    keyUpSpy = mocker.patch('src.utils.keyboard.keyUp')
    pressSpy = mocker.patch('src.utils.keyboard.press')
    leftClickSpy = mocker.patch('src.utils.mouse.leftClick')
    task = ClickInClosestCreatureTask()
    assert task.do(context) == context
    keyDownSpy.assert_called_once_with('alt')
    leftClickSpy.assert_called_once_with(context['ng_cave']['closestCreature']['windowCoordinate'])
    keyUpSpy.assert_called_once_with('alt')
    pressSpy.assert_not_called()

def test_should_do_and_ignore_hotkey_attack_when_there_ignorable_creatures(mocker):
    context = {
        'ng_cave': {'closestCreature': {'windowCoordinate': (0, 0)}},
        'gameWindow': {'players': []},
        'ng_targeting': {'hasIgnorableCreatures': True}
    }
    keyDownSpy = mocker.patch('src.utils.keyboard.keyDown')
    keyUpSpy = mocker.patch('src.utils.keyboard.keyUp')
    pressSpy = mocker.patch('src.utils.keyboard.press')
    leftClickSpy = mocker.patch('src.utils.mouse.leftClick')
    task = ClickInClosestCreatureTask()
    assert task.do(context) == context
    keyDownSpy.assert_called_once_with('alt')
    leftClickSpy.assert_called_once_with(context['ng_cave']['closestCreature']['windowCoordinate'])
    keyUpSpy.assert_called_once_with('alt')
    pressSpy.assert_not_called()

def test_should_do_and_press_space_hotkey_when_there_is_no_players_or_ignorable_creatures(mocker):
    context = {
        'ng_cave': {'closestCreature': {'windowCoordinate': (0, 0)}},
        'gameWindow': {'players': []},
        'ng_targeting': {'hasIgnorableCreatures': False}
    }
    pressSpy = mocker.patch('src.utils.keyboard.press')
    task = ClickInClosestCreatureTask()
    assert task.do(context) == context
    pressSpy.assert_called_once_with('space')
