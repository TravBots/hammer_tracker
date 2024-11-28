import discord
from discord import app_commands
from utils.constants import Colors, crop_production


@app_commands.command()
@app_commands.choices(
    cropper_type=[
        app_commands.Choice(name="6 Crop", value=6),
        app_commands.Choice(name="7 Crop", value=7),
        app_commands.Choice(name="9 Crop", value=9),
        app_commands.Choice(name="15 Crop", value=15),
    ]
)
@app_commands.choices(
    gold_bonus=[
        app_commands.Choice(name="Yes", value=0.0),
        app_commands.Choice(name="No", value=0.25),
    ]
)
@app_commands.choices(
    oasis_bonus=[
        app_commands.Choice(name="0%", value=0.0),
        app_commands.Choice(name="25%", value=0.25),
        app_commands.Choice(name="50%", value=0.50),
        app_commands.Choice(name="75%", value=0.75),
        app_commands.Choice(name="100%", value=1.00),
        app_commands.Choice(name="125%", value=1.25),
        app_commands.Choice(name="150%", value=1.50),
    ]
)
@app_commands.choices(
    flour_mill_bakery=[
        app_commands.Choice(name="5%", value=0.05),
        app_commands.Choice(name="10%", value=0.10),
        app_commands.Choice(name="15%", value=0.15),
        app_commands.Choice(name="20%", value=0.20),
        app_commands.Choice(name="25%", value=0.25),
        app_commands.Choice(name="30%", value=0.30),
        app_commands.Choice(name="35%", value=0.35),
        app_commands.Choice(name="40%", value=0.40),
        app_commands.Choice(name="45%", value=0.45),
        app_commands.Choice(name="50%", value=0.50),
    ]
)
@app_commands.choices(
    field_levels=[
        app_commands.Choice(name="10", value=10),
        app_commands.Choice(name="11", value=11),
        app_commands.Choice(name="12", value=12),
        app_commands.Choice(name="13", value=13),
        app_commands.Choice(name="14", value=14),
        app_commands.Choice(name="15", value=15),
        app_commands.Choice(name="16", value=16),
        app_commands.Choice(name="17", value=17),
        app_commands.Choice(name="18", value=18),
        app_commands.Choice(name="19", value=19),
        app_commands.Choice(name="20", value=20),
    ]
)
@app_commands.describe(
    crop_1="Amount of crop scouted in first report",
    crop_2="Amount of crop scouted in second report",
    seconds_between_scoutings="The number of seconds between the first and second scout report",
    cropper_type="Crop type of village",
    field_levels="Level of crop fields in the village",
    oasis_bonus="Crop bonus from oases",
    reins_in_village="Wheat count of all troops present in target village",
    population="Population of the target village",
    flour_mill_bakery="Crop bonus from flour mill and bakery. Default: 50%",
    gold_bonus="Does the defender have the gold bonus activated? Default: Yes",
)
async def scout(
    interaction: discord.Interaction,
    crop_1: int,
    crop_2: int,
    seconds_between_scoutings: int,
    field_levels: int,
    oasis_bonus: float,
    reins_in_village: int,
    population: int,
    cropper_type: int,
    flour_mill_bakery: float = 0.50,
    gold_bonus: float = 0.25,
):
    """Calculate a crop scout"""
    base_production = crop_production[field_levels] * cropper_type
    with_oases_mill_bakery = (
        (base_production * oasis_bonus)
        + (base_production * flour_mill_bakery)
        + base_production
    )
    with_gold_bonus = with_oases_mill_bakery * (1 + gold_bonus)
    hammer_size = (
        (((crop_1 - crop_2) / seconds_between_scoutings) * 3600)
        - reins_in_village
        + with_gold_bonus
        - population
    )

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Crop Scout Result",
        value=f"Expected hammer size (in crop consumption): **{int(hammer_size):,}**",
    )
    await interaction.response.send_message(embed=embed)
