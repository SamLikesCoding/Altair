import glob
import os

# Poetry


def argvalid(prompt_mesg, error_prompt, default_value=''):
    while True:
        var = input(prompt_mesg)
        if var == '':
            if default_value != '':
                return default_value
            print(error_prompt)
        else:
            return var


class projectSeed:

    def __init__(self, project_id, author, path="./"):
        self.proj_id = project_id
        self.author = author
        self.dirs = []
        self.files = {}
        self.creatree(path)

    def creatree(self, path):
        items = glob.glob(os.path.join(path, "*"))
        for item in items:
            if os.path.isdir(item):
                print("DIR : {}".format(item))
                self.dirs.append(item)
                self.creatree(item)
            if os.path.isfile(item):
                print("FILE : {}".format(item))
                buffer = None
                with open(item, "rb") as feeder:
                    buffer = feeder.read()
                self.files[item] = buffer

    def artifact(self):
        return {
            "Project_ID": self.proj_id,
            "author": self.author,
            "dirs": self.dirs,
            "files": self.files
        }

    def size(self):
        prj_size = 0
        for pfile in self.files.keys():
            prj_size += len(self.files[pfiles])
        return prj_size

    def __str__(self):
        return "\n------\nProject : {}\nAuthor : {}\n------\nDirectories : {}\nFiles : {}\n".format(
            self.proj_id, self.author,
            len(self.dirs), len([x for x in self.files.keys()])
        )


if __name__ == "__main__":
    proj_id = argvalid("Enter Project ID : ",
                       "=(!)=== Project ID should not be null ===(!)=")
    author = argvalid("Enter Author Name : ",
                      "=(!)=== Author field should not be null ===(!)=")
    path = argvalid("Enter Project Path (Default : ./): ", "", './')
    project = projectSeed(proj_id, author, path)
    print(project)
    print(len(project.artifact()))
