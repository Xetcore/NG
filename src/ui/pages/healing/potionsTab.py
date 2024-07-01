from .healthPotionCard import HealthPotionCard
from .manaPotionCard import ManaPotionCard
import customtkinter

class PotionsTab(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.healthPotionCard = HealthPotionCard(
            self, context, 'firstHealthPotion', title='Health potion')
        self.healthPotionCard.grid(column=0, row=0, padx=10,
                                pady=10, sticky='nsew')

        self.manaPotionCard = ManaPotionCard(
            self, context, 'firstManaPotion', title='Mana potion')
        self.manaPotionCard.grid(column=1, row=0, padx=10,
                                pady=10, sticky='nsew')
