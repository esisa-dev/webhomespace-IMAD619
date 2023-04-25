import os
import subprocess
import zipfile
from model import dossier

class Services:
    index: dict = {}
    _user:str

    def getContent(self, folder: str) -> dict:
        if not self.index:
            path = "/home/" + folder
            self.index[path] = []
        else:
            first_key = next(iter(self.index))
            path = "/" + folder
            new_key=first_key+path
            self.index={}
            self.index[new_key]=[]
        
        first_key = next(iter(self.index))
        output = subprocess.check_output(['ls', '-l', '--time-style=+%d/%m/%Y', first_key])
        dossiers = []
        output_lines = output.decode().split('\n')
        for line in output_lines:
            res = line.split()
            if len(res) == 7:
                dossiers.append(dossier(res[0], res[1], res[2], res[3], res[4],
                                            res[5] ,res[6]))
        self.index[list(self.index.keys())[0]] = dossiers
        

    def rechercher(self,keyword):
        dossiers = []
        if self.index=={}:
            return []
        else:
            first_key = next(iter(self.index))
            for val in self.index[first_key]:
                if keyword in val.name or keyword==val :
                    dossiers.append(val)
            return dossiers
    
    def get_nb_of_Dirs(self)->dict:
        dic_nb={}
        dic_nb["Dirs"]=0
        dic_nb["Files"]=0
        dic_nb["Space"]=0
        first_key = next(iter(self.index))
        for val in self.index[first_key]:
            if val.permission.startswith('d'):
                dic_nb["Dirs"]+=1
            else:
                dic_nb["Files"]+=1
            dic_nb["Space"]+=int(val.taille)
        return dic_nb
    
    def get_nb_of_Dirs_by_Keyword(self,Keyword)->dict:
        dossiers = self.rechercher(Keyword)
        dic_nb={}
        dic_nb["Dirs"]=0
        dic_nb["Files"]=0
        dic_nb["Space"]=0
        for val in dossiers:
            if val.permission.startswith('d'):
                dic_nb["Dirs"]+=1
            else:
                dic_nb["Files"]+=1
            dic_nb["Space"]+=int(val.taille)
        return dic_nb
    
    def Connecter_User(self,username, password) -> bool:
        try:
            command = ["su", "-c", "whoami", username]
            self._user=username
            result = subprocess.run(command, input=password.encode(), capture_output=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
        
    def Creer_User(self, username:str, password1:str, password2:str)->str:
        result = subprocess.run(['id', '-u', username], stdout=subprocess.PIPE)
        if result.returncode == 0:
            return 'L utilisateur existe déjà'
        if password1==password2:
            subprocess.run(['sudo', 'useradd', '-p', password1, username])
            return 'Utilisateur bien ajouté'
        else:
            return 'Les deux mots de passe ne sont pas identiques'
    
    def Compresser_zip(self):
        home_dir = "/home/" + self._user
        zip_filename = self._user + ".zip"
        zip_filepath = os.path.join(home_dir, zip_filename)
        with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root,dirs, files in os.walk(home_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        zip_file.write(file_path, os.path.relpath(file_path, home_dir))
                    except FileNotFoundError:
                        print(f"Ignoré le fichier {file_path} qui n'existe pas.")
        return zip_filepath
    
    def Cat_File(self,file)->str:
        try:
            with open(file, 'r') as f:
                contenu = f.read()
            return contenu
        except FileNotFoundError:
            return "Le fichier spécifié n'existe pas."
        
    def modifier_key(self)->str:
        first_key = next(iter(self.index))
        d=self.index[first_key]
        index_dernier_slash = first_key.rfind("/")
        if index_dernier_slash != -1:
            first_key = first_key[:index_dernier_slash]
            if first_key[-1] == "/":
                first_key = first_key[:-1]
        self.index={}
        self.index[first_key]=d

        output = subprocess.check_output(['ls', '-l', '--time-style=+%d/%m/%Y', first_key])
        dossiers = []
        output_lines = output.decode().split('\n')
        for line in output_lines:
            res = line.split()
            if len(res) == 7:
                dossiers.append(dossier(res[0], res[1], res[2], res[3], res[4],
                                            res[5] ,res[6]))
        self.index[list(self.index.keys())[0]] = dossiers