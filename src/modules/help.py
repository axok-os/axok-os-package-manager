"""

AOPM help Module
-----------------
Description: Module used to display help messages about modules, repositories, and the AOPM core
Made by: GusDev
Version: 1.0.0

"""

# imports
import aopmAPI

# To a AOPM Module works well you will need some functions (defs)

# 1 - get_header():
#           Used to return the aopmAPI manifest, that contains informations about the module, like name, version, author,
#       description and the api_version
#           That is used to the API read your informations, if something is missing or wrong, it wont be executed.
#       The manifest is what tells to AOPM that is a AOPM Module.

def get_header() -> dict:
	"""
	Return the aopmAPI manifest

	:return: dict
	"""
	return {
		"name": "help",
		"version": "1.0.0",
		"description": "display help information about modules, repositories or of AOPM core.",
		"author": "GusDev",
		"author_email": "axok.os.team@gmai.com",
		"api_version": "1.0.0"
	}