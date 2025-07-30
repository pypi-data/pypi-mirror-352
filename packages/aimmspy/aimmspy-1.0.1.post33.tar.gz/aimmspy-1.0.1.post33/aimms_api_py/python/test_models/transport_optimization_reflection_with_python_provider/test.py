
import aimms_api_py as aap

# Open a file in write mode
with open("globals.txt", "w") as file:
    # Write "Hello, World!" to the file
    file.write(str(globals()))

with open("locals.txt", "w") as file:
    # Write "Hello, World!" to the file
    file.write(str(locals()))

try:
# print("Test file created with 'Hello, World!'")
    my_aimms = aap.AimmsAPI.get_current_aimms_api()
    with open("my_aimms.txt", "w") as file:
        # Write "Hello, World!" to the file
        file.write(str(my_aimms.exposed_identifier_set))
except Exception as e:
    with open("exception.txt", "w") as file:
        # Write "Hello, World!" to the file
        file.write(str(e))
# with open("my_aimms.txt", "w") as file:
#     # Write "Hello, World!" to the file
#     file.write(str(vars(my_aimms)))

# print ("Hello, World!")
# open("file.txt", "w").write("Hello, world!") and None
