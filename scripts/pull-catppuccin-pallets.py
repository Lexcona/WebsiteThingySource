import requests

from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

console.print("Grabbing pallets page...", style="cyan")

res = requests.get("https://catppuccin.com/palette/")
res.raise_for_status()

console.print("Got pallet page :3", style="green")

soup = BeautifulSoup(res.content, "html.parser")

class PalletData:
    def __init__(self, name:str):
        self.name = name
        self.colors = []

class ColorData:
    def __init__(self, name:str, color:str):
        self.name = name
        self.color = color

pallets = []

for flavor in soup.find_all("div", class_="flavor"):
    flavor_id = ""
    colors = []

    flavor_name_h2 = flavor.find("h2", class_="flavor-name")
    if not flavor_name_h2:
        console.print("Failed to get flavor_name_h2 :(", style="red")
        continue

    flavor_names = flavor_name_h2.find_all("span")
    for flavor_name in flavor_names:
        flavor_id = flavor_name.get("data-flavor")
        if flavor_id:
            break

    if not flavor_id:
        console.print("Failed to get flavor_id :(", style="red")
        continue
    else:
        console.print(f"Got flavor_id :3 {flavor_id}", style="cyan")

    pallet = PalletData(flavor_id)

    color_list_table = flavor.find("table", class_="color-list")
    if not color_list_table:
        console.print("Failed to get color-list :(", style="red")
        continue

    console.print(f"Getting colors...", style="cyan")

    for color in color_list_table.find_all("tr", class_="color-list-entry"):
        color_data = ColorData(color.find("h5", class_="color-name").text, color.find("astro-slot").text)
        console.print(f"Got color :3 {color_data}", style="green")
        pallet.colors.append(color_data)

    pallets.append(pallet)

for pallet in pallets:
    path = f"static/styles/pallets/catppuccin/{pallet.name}.css"

    console.print(f"Writing {path}", style="cyan")

    css_file = ":root {\n"
    for color in pallet.colors:
        css_file += f"    --{color.name.replace(" ", "-").lower()}: {color.color};\n"
    css_file += "}"

    with open(path, "w+") as f:
        f.write(css_file)

    console.print(f"Wrote {path} :3", style="green")