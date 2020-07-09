import os
import sys
import inspect
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.utils import iface
from qgis.core import *

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]


#Create class for the checkbox:
class CheckBox(QWidget):
    def __init__(self, parent=None):
        self.iface = iface
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()

        # Add the radio buttons
        self.change = QRadioButton("Changer le nom d'une colonne")
        self.add = QRadioButton('Ajouter une colonne')
        self.delete = QRadioButton('Supprimer une colonne')
        self.copy = QRadioButton('Copier une colonne')

        # Connect radio buttons to our functions
        self.change.toggled.connect(self.change_active)
        self.delete.toggled.connect(self.delete_active)
        self.add.toggled.connect(self.add_active)
        self.copy.toggled.connect(self.copy_active)

        #Add the widgets to the layout:
        self.layout.addWidget(self.change)
        self.layout.addWidget(self.add)
        self.layout.addWidget(self.delete)
        self.layout.addWidget(self.copy)

        #Set the layout:
        self.setLayout(self.layout)
        
        self.group = QButtonGroup()
        self.group.addButton(self.change)
        self.group.addButton(self.delete)
        self.group.addButton(self.add)
        self.group.addButton(self.copy) 
        self.setWindowTitle("Actions basiques")        

        
    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
      self.action = QAction(QIcon(icon), 'Actions basiques QGis', self.iface.mainWindow()) #written when hovered
      self.action.triggered.connect(self.run) #runs run() when clicked
      self.iface.addPluginToMenu('&Actions basiques', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)       
      self.iface.removePluginMenu('&Actions basiques', self.action)  
      del self.action  

    def run(self):
      buttons.show() #shows our widgets
      self.iface.messageBar().pushMessage("L'extension QGis basics a été lancée")

    # First radio buttons
    def change_active(self, on):
        if on:
            ##print("changing")
            self.close() #ferme la checkbox
            layer = iface.activeLayer()
            prov = layer.dataProvider()
            items = ([field.name() for field in prov.fields()])
            item, ok = QInputDialog.getItem(self, "Sélectionnez un nom à changer", 
         "Liste des champs", items, 0, False) # get field to delete with selector
            if ok and item:
                change_name(item) # send name of the field to function
            else : 
                #print("Pas de champ entré")
                iface.messageBar().pushWarning("Erreur", "Vous n'avez pas entré de champ à changer")
            self.group.setExclusive(False)   #3 lines to uncheck the button (for next use) 
            self.change.setChecked(False) 
            self.group.setExclusive(True)


    # Second radio buttons    
    def delete_active(self, on):
        if on:
            ##print("delete")
            self.close()
            layer = iface.activeLayer()
            prov = layer.dataProvider()
            items = ([field.name() for field in prov.fields()])
            item, ok = QInputDialog.getItem(self, "Sélectionnez un champ à supprimer", 
         "Liste des champs", items, 0, False) # get field to delete with selector
            if ok and item:
                delete_column(item) # send name of the field to function
            else : 
                #print("Pas de champ entré")
                iface.messageBar().pushWarning("Erreur", "Vous n'avez pas entré de champ à supprimer")
            self.group.setExclusive(False)    
            self.delete.setChecked(False) 
            self.group.setExclusive(True)

    
    #Third radio buttons
    def add_active(self, on):
        if on :
            ##print("adding")
            self.close()
            add_column()
            self.group.setExclusive(False)    
            self.add.setChecked(False) 
            self.group.setExclusive(True)
        
        
    def copy_active(self, on):
        if on :
            ##print("copying")
            self.close()
            layer = iface.activeLayer()
            prov = layer.dataProvider()
            items = ([field.name() for field in prov.fields()])
            field_to_copy, ok = QInputDialog.getItem(self, "Sélectionnez le champ à copier", 
         "Copier les valeurs de...", items, 0, False) # get field to delete with selector
            if ok and field_to_copy:
                items = ([field.name() for field in prov.fields()])
                field_to_paste, ok = QInputDialog.getItem(self, "Sélectionner le champ pour coller", 
             "Coller les valeurs dans...", items, 0, False) 
                #print(field_to_copy)
                if ok and field_to_paste:
                    #print(field_to_paste)
                    #print(field_to_copy, field_to_paste)
                    copy_column(field_to_copy, field_to_paste)  
                else : 
                    #print("Pas de champ entré")
                    iface.messageBar().pushWarning("Erreur", "Vous n'avez pas entré de champ à coller")
            else : 
                #print("Pas de champ entré")
                iface.messageBar().pushWarning("Erreur", "Vous n'avez pas entré de champ à copier")
            self.group.setExclusive(False)    
            self.copy.setChecked(False) 
            self.group.setExclusive(True)
  
buttons = CheckBox()





##########  OTHER FUCNTIONS USED ##########

#Input used in functions that require an entry by the user
def getTextInput(title, message):
    answer = QInputDialog.getText(None, title, message)
    if answer[1]:
        ##print(answer[0])
        return answer[0]
    else:
        return None



#Function to change the name of a column
def change_name(old_name):
    layer = iface.activeLayer()
    check=0
    for field in layer.fields():
        if field.name() == old_name:
            new_name=getTextInput('Modifier un nom de colonne', "Veuillez entrer le nouveau nom de colonne")
            if new_name==None : #no name entered
                check=0
                continue;
                    
            field_index = layer.fields().indexFromName(new_name) # l'id de la colonne avec le nom new_name
            if field_index == -1 and new_name!=None:                
                id = layer.fields().indexFromName(field.name())
                layer.startEditing() #entering edition mode
                layer.renameAttribute(id, new_name)
                layer.commitChanges() #commiting changes
                iface.vectorLayerTools().stopEditing(layer) #exit edition mode
                #print("La colonne {} s'appelle maintenant {}".format(old_name, new_name))
                iface.messageBar().pushSuccess("Succes", "Le nom de la colonne a bien été modifiée")
                check=1
            else:                 
                #print("La colonne {} existe déjà dans {}".format(new_name, layer.name()))
                iface.messageBar().pushWarning("Erreur", "Ce nom de colonne existe déjà")
                check=1
            
    if check == 0:
        iface.messageBar().pushWarning("Erreur", "Le nom de la colonne à changer n'a pas été trouvée") 


#Fonction : creer 3 colonnes puis copier des valeurs dans une
def add_column():
    layer = iface.activeLayer()


    field_name = getTextInput('Ajouter une colonne', 'Veuillez entrer le nom de la colonne à ajouter') 
    field_to_add = layer.fields().indexFromName(field_name)
    prov = layer.dataProvider()
    field_names = [field.name() for field in prov.fields()]
      

    if field_to_add == -1 :
        adding_test = layer.dataProvider().addAttributes([ QgsField(field_name, QVariant.String) ])
        if adding_test == False:
            #print("Un problème est survenu")
            iface.messageBar().pushWarning("Erreur", "Un problème est survenu")
        else:
            #print("La colonne '", field_name, "' a été ajoutée")
            iface.messageBar().pushSuccess("Succès", "La colonne a été ajoutée")
    else : 
        #print("La colonne numero ", field_to_add, " (", field_name, ") existe déjà")
        iface.messageBar().pushWarning("Erreur", "Cette colonne existe déjà")
    layer.updateFields()



#Function to delete a column
def delete_column(field_name):
    layer = iface.activeLayer()
    field_to_delete = layer.fields().indexFromName(field_name)

    if field_to_delete == -1 :
        iface.messageBar().pushWarning("Erreur", "La colonne n'a pas pu être trouvée")
        #print("La colonne '", field_name, "' n'a pas pu être trouvée")
    else : 
        delete_test = layer.dataProvider().deleteAttributes([field_to_delete])  
        if delete_test == True : 
            #print("La colonne numero ", field_to_delete, " (", field_name, ") a été supprimée")
            iface.messageBar().pushSuccess("Succès", "La colonne a été supprimée")       
        else : 
            #print("Un problème est survenu")
            iface.messageBar().pushWarning("Erreur", "Un problème est survenu")
    
    layer.updateFields()
    


#Function to copy the values of a column and add them in another column
def copy_column(field_to_copy, field_to_paste):
    layer = iface.activeLayer()
        
    id_field_to_copy = layer.fields().indexFromName(field_to_copy) # retourne -1 si l'id n'existe pas
    id_field_to_paste = layer.fields().indexFromName(field_to_paste)
    
    #print("copier : ", id_field_to_copy, " coller : ", id_field_to_paste)
    
    if id_field_to_copy != -1 and field_to_paste != -1:
        layer.startEditing()
        for feature in layer.getFeatures():
            feature.setAttribute(feature.fieldNameIndex(field_to_paste), feature[field_to_copy])
            layer.updateFeature(feature)
        layer.commitChanges()
        iface.vectorLayerTools().stopEditing(layer)
        iface.messageBar().pushSuccess("Succès", "Les valeurs ont été copiées")
        #print("Les valeurs de la colonne {} ont bien été copiées dans {}".format(field_to_copy, field_to_paste))
