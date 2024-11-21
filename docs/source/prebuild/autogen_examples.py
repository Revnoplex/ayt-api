import os

specific_title_mapping = {
    "oauth2": "Initialising with OAuth2",
    "oauth2-auth-code": "Initialising using OAuth2 Authorisation Code",
    "oauth2-generator": "Initialising using OAuth2 Generator Function",
    "oauth2-token": "Initialising using OAuth2 Token",
    "search": "Running a Search"
}


def main():
    with open("usage/examples.md", "w") as examples:
        examples.write("# Examples\n\n")
        print(os.listdir("../../examples"))
        for example in sorted(os.listdir("../../examples")):
            print(example)
            example_name = example.split(".")[0]
            example_title = f"Fetching Information on a {example_name.replace('-', ' ').title()}"
            if "-" in example_name:
                prefix, suffix = example_name.split('-')[0].title(), " ".join(example_name.split('-')[1:]).title()
                example_title = (
                    f"Fetching {suffix} from a {prefix}"
                )
                if example_name.startswith("update"):
                    example_title = f"Updating Metadata for a {suffix}"
            if example_name in specific_title_mapping:
                example_title = specific_title_mapping[example_name]

            examples.write(
                f"## {example_title}\n```{{literalinclude}} ../../../examples/{example}\n```\n\n"
            )
