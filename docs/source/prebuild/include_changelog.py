import copy


# Note: this algorithm only supports changing one link per line.
def main():
    print("prebuild [include_changelog]: Converting local references in changelog...")
    with open("../../CHANGELOG.md") as changelog_file:
        changelog_lines = changelog_file.readlines()
    updated_changelog = []
    for line in changelog_lines:
        has_characters_in_order = False
        modified_line = copy.copy(line)
        link_location = [0, 0]
        current_offset = 0
        for char in "[]()":
            if char not in modified_line:
                break
            if char == "[":
                link_location[0] = modified_line.index(char)
            current_offset += modified_line.index(char)
            if char == ")":
                has_characters_in_order = True
                link_location[1] = modified_line.index(char) + current_offset
            modified_line = modified_line[modified_line.index(char):]
        if has_characters_in_order:
            str_link = (line[link_location[0]:link_location[1]])[:-2]
            link_part = str_link[str_link.index("(")+1:str_link.index(")")]
            if not link_part.startswith("https://"):
                line = (
                    line[:link_location[0]+str_link.index("(")+1] + "https://github.com/Revnoplex/ayt-api/blob/main/" +
                    line[link_location[0]+str_link.index("(")+1:]
                )
        updated_changelog.append(line)
    print("prebuild [include_changelog]: Writing changelog...")
    with open("changelog.md", "w") as copied_changelog:
        copied_changelog.writelines(updated_changelog)
    print("prebuild [include_changelog]: Done")
