import re
from bs4 import BeautifulSoup, Tag, NavigableString

def find_table(soup: BeautifulSoup, table_class: str = "items") -> Tag:
    """
    Finds and returns the first table with the specified class.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object to search within.
        table_class (str, optional): The class of the table to find. Defaults to "items".

    Returns:
        Tag: The found table Tag object or None if not found.
    """
    try:
        table = soup.find("table", class_=table_class)
        if table:
            print(f"Found table with class '{table_class}'.")
            return table
        else:
            print(f"No table found with class '{table_class}'.")
            return None
    except Exception as e:
        print(f"Error finding table with class '{table_class}': {e}")
        return None

def extract_links_from_table(table: Tag, exclude_class: str = "bg_blau_20", 
                             td_class: str = "hauptlink no-border-links") -> list:
    """
    Extracts names and links from a table based on specified classes.

    Args:
        table (Tag): The BeautifulSoup Tag object representing the table.
        exclude_class (str, optional): The class to exclude rows. Defaults to "bg_blau_20".
        td_class (str, optional): The class of the <td> containing the link. Defaults to "hauptlink no-border-links".

    Returns:
        list: A list of dictionaries with 'name' and 'link' keys.
    """
    data = []
    try:
        tbody = table.find("tbody")
        if not tbody:
            print("Table body <tbody> not found.")
            return data

        rows = tbody.find_all("tr", class_=lambda x: x != exclude_class)
        print(f"Found {len(rows)} rows excluding class '{exclude_class}'.")

        for row in rows:
            td = row.find("td", class_=td_class.split()[0])  # Assuming first class is unique
            if td:
                a_tag = td.find("a", href=True)
                if a_tag:
                    name = a_tag.get_text(strip=True)
                    link = a_tag['href']

                    data.append({"name": name, "link": link})
                    print(f"Extracted: Name='{name}', Link='{link}'")
    except Exception as e:
        print(f"Error extracting links from table: {e}")
    return data

def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Converts a relative URL to an absolute URL based on the base URL.

    Args:
        base_url (str): The base URL of the website.
        relative_url (str): The relative URL to convert.

    Returns:
        str: The absolute URL.
    """
    if relative_url.startswith("http"):
        return relative_url
    return f"{base_url}{relative_url}"

def find_label_content(soup: BeautifulSoup, label_regex: str, content_class: str = "info-table__content--bold") -> str:
    """
    Finds the content corresponding to a label using regex.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object to search within.
        label_regex (str): The regex pattern to match the label text.
        content_class (str, optional): The class of the content span. Defaults to "info-table__content--bold".

    Returns:
        str: The extracted text content or None if not found.
    """
    try:
        label = soup.find("span", text=re.compile(label_regex, re.I))
        if label:
            content = label.find_next_sibling("span", class_=content_class)
            if content:
                return content.get_text(strip=True)
    except Exception as e:
        print(f"Error finding label '{label_regex}': {e}")
    return None

def parse_player_name(header: Tag) -> dict:
    """
    Parses the player's first name and last name from the header.

    Args:
        header (Tag): The BeautifulSoup Tag object representing the header.

    Returns:
        dict: A dictionary with 'nome' and 'cognome' keys.
    """
    nome = ""
    cognome = ""
    try:
        for child in header.children:
            if isinstance(child, NavigableString):
                text = child.strip()
                if text:
                    nome = text
            elif child.name == "strong":
                cognome = child.get_text(strip=True)
    except Exception as e:
        print(f"Error parsing player name: {e}")
    return {"nome": nome, "cognome": cognome}

def extract_nationalities(nazionalita_span: Tag) -> list:
    """
    Extracts the list of nationalities from the given span.

    Args:
        nazionalita_span (Tag): The BeautifulSoup Tag object containing nationality images.

    Returns:
        list: A list of nationality names.
    """
    nazionalita = []
    try:
        nazionalita = [img["title"] for img in nazionalita_span.find_all("img", alt=True)]
    except Exception as e:
        print(f"Error extracting nationalities: {e}")
    return nazionalita

def extract_altri_ruoli(detail_position: Tag) -> list:
    """
    Extracts the list of other roles from the detail position box.

    Args:
        detail_position (Tag): The BeautifulSoup Tag object representing the detail position box.

    Returns:
        list: A list of other roles.
    """
    altri_ruoli = []
    try:
        altri_ruoli_label = detail_position.find("dt", text=re.compile(r"Altro ruolo:", re.I))
        if altri_ruoli_label:
            altri_ruoli_dds = altri_ruoli_label.find_next_siblings("dd")
            if altri_ruoli_dds:
                altri_ruoli = [dd.get_text(strip=True) for dd in altri_ruoli_dds]
    except Exception as e:
        print(f"Error extracting other roles: {e}")
    return altri_ruoli

def extract_player_details_from_header(header: Tag) -> dict:
    """
    Extracts player's shirt number, first name, and last name from the header.

    Args:
        header (Tag): The BeautifulSoup Tag object representing the header.

    Returns:
        dict: A dictionary with 'numero_maglia', 'nome', and 'cognome' keys.
    """
    details = {"numero_maglia": None, "nome": None, "cognome": None}
    try:
        numero_maglia_span = header.find("span", class_="data-header__shirt-number")
        if numero_maglia_span:
            numero_maglia = numero_maglia_span.get_text(strip=True).replace("#", "")
            details["numero_maglia"] = numero_maglia

        name_parts = parse_player_name(header)
        details.update(name_parts)
    except Exception as e:
        print(f"Error extracting player details from header: {e}")
    return details

def extract_value_from_div(valore_div: Tag, value_class: str, fallback: bool = False) -> str:
    """
    Extracts a value from a div based on the provided class.

    Args:
        valore_div (Tag): The BeautifulSoup Tag object representing the value div.
        value_class (str): The class to search for within the div.
        fallback (bool, optional): If True, applies fallback logic. Defaults to False.

    Returns:
        str: The extracted value or None if not found.
    """
    try:
        value_tag = valore_div.find("div", class_=re.compile(value_class))
        if value_tag:
            a_tag = value_tag.find("a")
            if a_tag:
                return a_tag.get_text(strip=True)
            else:
                return value_tag.get_text(strip=True)
    except Exception as e:
        print(f"Error extracting value with class '{value_class}': {e}")
    return None
