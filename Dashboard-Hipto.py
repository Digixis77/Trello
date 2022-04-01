import numpy as np 
import pandas as pd 
import json 
import streamlit as st
import requests 
import datetime



st.title('Trello Dashboard')

today = datetime.datetime.now()
day_last_week = today - datetime.timedelta(7)
day_last_month =  today - datetime.timedelta(30)


#@st.cache
#def load_data(URL):
    #with open(URL) as f:
        #data = json.load(f)
    #return data

#fonction qui permet d'ajouter une colonne avec les labels dans une même chaîne de caractère 
def label_name(colonnes,df):
    colonnes.astype(str)
    c= count_rows(colonnes)
    colonnes.index = [k for k in range(0,c)]
    df.index = [k for k in range(0,c)]
    df['label_name'] = ''
    df['label_name'].astype(str)
    for i in range(0,c):
        x = colonnes[i]
        for j in range(len(x)):
            print(df['label_name'][i])
            if df['label_name'][i] == 'NaN': 
                df['label_name'][i] = x[j]['name'] + " " + x[j]['color']
            else :
                df['label_name'][i] = df['label_name'][i] + " " + x[j]['name'] + " " + x[j]['color']
    return df['label_name']

#fonction qui permet de compter le nombre de ligne  
def count_rows(rows):
    return len(rows)

#fonction qui permet de compter les élémenst d'une liste
def count_elements(list):
    return len(list)


#trie le dataframe en fonction des labels 
def trie(df, L):
    df2 = df.copy()
    for i in L:
        mask = df2['label_name'].str.contains(i)
        df2 = df2[mask]
    return len(df2)

#permet de mettre en place la sidebar 
st.sidebar.title('Quel est votre BU ?')
option = st.sidebar.selectbox('selectionnez la BU',('BPO', 'Mutuelle', 'Formation', 'Assurance','Travaux'))


# code pour le BU BPO
if option == 'BPO':
    
    
    #création du dataframe des listes présentes sur le Trello
    url2 = "https://api.trello.com/1/boards/FFBh4bD2/lists?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url2)
    df_list = response.json()
    df_list = pd.json_normalize(df_list)

    
    #génération du dataframe des membres du tableau Trello
    url1 = "https://api.trello.com/1/boards/FFBh4bD2/members?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url1)
    df_members = response.json()
    df_members = pd.json_normalize(df_members)


    #génération du dataframe des cartes présentes sur le Trello
    url = "https://sirin.hipto.com/index.php/Sandbox/frederick_trello_one?bordname=bubpo"
    reponse = requests.get(url)
    df_cards = reponse.json()
    df_cards = pd.json_normalize(df_cards)

    if st.sidebar.button('Afficher semaine passée'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_week = pd.to_datetime(day_last_week)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_week) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]

    if st.sidebar.button('Afficher mois passé'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_month = pd.to_datetime(day_last_month)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_month) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]
    

    #Travail sur l'id des membres du tableau
    df_cards['idMembers'] = df_cards['idMembers'].astype(str)
    df_cards['idMembers'] = df_cards['idMembers'].apply(lambda x: x.replace("['","").replace("']",''))
    df_members['id'] = df_members['id'].astype(str)

    #création d'un dataframe avec cartes et membres
    df_cards_members = pd.merge(df_members, df_cards, left_on = ['id'],right_on = ['idMembers'])
    df_cards_members_list = pd.merge(df_list,df_cards_members, left_on =['id'] ,right_on =['idList'] )
    df_cards_members_list_total = df_cards_members_list

    #création d'un tableau contenant les infos uniquement des cartes dans Winnings Historique
    df_cards_members_list_mask = df_cards_members_list['name_x'] == 'Winnings historique'
    df_cards_members_list = df_cards_members_list[df_cards_members_list_mask]

    #Génération du datfarame des labels
    url3 = "https://api.trello.com/1/boards/FFBh4bD2/labels?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url3)
    df_labels= response.json()
    df_labels = pd.json_normalize(df_labels)
    df_labels = df_labels[['id','name','color']]
    c = count_rows(df_labels)
    for i in range (0,c):
        df_labels['label_complet'] = df_labels['name'] + " " + df_labels['color']

    #code permettant d'avoir les labels dans la sidebar (sans les verticales)   
    labels = df_labels['label_complet']
    mask_label_complet = df_labels['label_complet'].str.contains("green")
    df_labels = df_labels[mask_label_complet == False]
    labels = df_labels['label_complet']

    #code permettant de récupérer le nombres de créa présentes sur les cartes 
    label_name(df_cards_members_list['labels'],df_cards_members_list)
    label_name(df_cards_members_list_total['labels'],df_cards_members_list_total)
    df_cards_members_list['nbCrea'] = df_cards_members_list['badges.attachments']
    df_nbAttachments = df_cards_members_list.groupby(['fullName']).sum()
    df_nbAttachments = df_nbAttachments['nbCrea']
    df_cards_members['nbCrea'] = df_cards_members['badges.attachments']
    df_nbAttachments2 = df_cards_members.groupby(['fullName']).sum()
    df_nbAttachments2 = df_nbAttachments2['nbCrea']
    
    #génération de la barre de multiselection 
    data_label_selected = st.multiselect('labels Winnings Historique',labels)
    
    #génération du dataframe pour les tableaux 
    columns = ['Le nombre de Winnings Historique','Le nombre de créa', '%']
    columns2 = ['Le nombre de Winnings Historique', 'Le nombre de carte', '%']
    index = df_nbAttachments.index
    index2 = ['FIB green','MOB green','NRJ green','NRJ.FIB green','NRJita green']
    
    

    #Premier tableau (Créa et Winnings par personne)
    response = pd.DataFrame(index = index, columns = columns)
    response['Le nombre de Winnings Historique'] = df_nbAttachments
    response['Le nombre de créa'] = df_nbAttachments2
    response['%'] = response['Le nombre de Winnings Historique']/response['Le nombre de créa']*100

    #Deuxième tableau Créa et Winnings par étiquette
    response2 = pd.DataFrame(index = index2, columns = columns2 )
    response2['Le nombre de Winnings Historique'] = [trie(df_cards_members_list,["FIB green "]+ data_label_selected), trie(df_cards_members_list,["MOB green "]+ data_label_selected),trie(df_cards_members_list,["NRJ green "]+ data_label_selected), trie(df_cards_members_list,["NRJ.FIB green "]+ data_label_selected), trie(df_cards_members_list,["NRJita green "]+ data_label_selected)]
    response2['Le nombre de carte'] = [trie(df_cards_members_list_total,["FIB green "]+ data_label_selected), trie(df_cards_members_list_total,["MOB green "]+ data_label_selected), trie(df_cards_members_list_total,["NRJ green "]+ data_label_selected), trie(df_cards_members_list_total,["NRJ.FIB green "]+ data_label_selected), trie(df_cards_members_list_total,["NRJita green "]+ data_label_selected)]
    response2['%'] = response2['Le nombre de Winnings Historique']/response2['Le nombre de carte']*100

    st.markdown('## Cartes et Winnings par étiquette')
    
    st.write(response2)
    
    # tableau des Créa et Winnings par personne
    st.markdown("## Créa et Winnings par personne")
    st.write(response)
    st.markdown("Si une personne n'est pas dans le tableau alors elle n'a jamais fait de créa en Winnings Historique")

    

if option == "Mutuelle":
    #création du dataframe des listes présentes sur le Trello
    url2 = "https://api.trello.com/1/boards/V9Q1I9Qx/lists?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url2)
    df_list = response.json()
    df_list = pd.json_normalize(df_list)

    
    #génération du dataframe des membres du tableau Trello
    url1 = "https://api.trello.com/1/boards/V9Q1I9Qx/members?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url1)
    df_members = response.json()
    df_members = pd.json_normalize(df_members)


    #génération du dataframe des cartes présentes sur le Trello
    url = "https://sirin.hipto.com/index.php/Sandbox/frederick_trello_one?bordname=bumutuelle"
    reponse = requests.get(url)
    df_cards = reponse.json()
    df_cards = pd.json_normalize(df_cards)

    if st.sidebar.button('Afficher semaine passée'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_week = pd.to_datetime(day_last_week)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_week) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]

    if st.sidebar.button('Afficher mois passé'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_month = pd.to_datetime(day_last_month)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_month) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]
    

    #Travail sur l'id des membres du tableau
    df_cards['idMembers'] = df_cards['idMembers'].astype(str)
    df_cards['idMembers'] = df_cards['idMembers'].apply(lambda x: x.replace("['","").replace("']",''))
    df_members['id'] = df_members['id'].astype(str)

    #création d'un dataframe avec cartes et membres
    df_cards_members = pd.merge(df_members, df_cards, left_on = ['id'],right_on = ['idMembers'])
    df_cards_members_list = pd.merge(df_list,df_cards_members, left_on =['id'] ,right_on =['idList'] )
    df_cards_members_list_total = df_cards_members_list

    #création d'un tableau contenant les infos uniquement des cartes dans Winnings Historique
    df_cards_members_list_mask = df_cards_members_list['name_x'] == 'Winnings historique'
    df_cards_members_list = df_cards_members_list[df_cards_members_list_mask]

    #Génération du datfarame des labels
    url3 = "https://api.trello.com/1/boards/V9Q1I9Qx/labels?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url3)
    df_labels= response.json()
    df_labels = pd.json_normalize(df_labels)
    df_labels = df_labels[['id','name','color']]
    c = count_rows(df_labels)
    for i in range (0,c):
        df_labels['label_complet'] = df_labels['name'] + " " + df_labels['color']

    #code permettant d'avoir les labels dans la sidebar (sans les verticales)   
    labels = df_labels['label_complet']
    mask_label_complet = df_labels['label_complet'].str.contains("green")
    df_labels = df_labels[mask_label_complet == False]
    labels = df_labels['label_complet']

    #code permettant de récupérer le nombres de créa présentes sur les cartes 
    label_name(df_cards_members_list['labels'],df_cards_members_list)
    label_name(df_cards_members_list_total['labels'],df_cards_members_list_total)
    df_cards_members_list['nbCrea'] = df_cards_members_list['badges.attachments']
    df_nbAttachments = df_cards_members_list.groupby(['fullName']).sum()
    df_nbAttachments = df_nbAttachments['nbCrea']
    df_cards_members['nbCrea'] = df_cards_members['badges.attachments']
    df_nbAttachments2 = df_cards_members.groupby(['fullName']).sum()
    df_nbAttachments2 = df_nbAttachments2['nbCrea']
    
    #génération de la barre de multiselection 
    data_label_selected = st.multiselect('labels Winnings Historique',labels)
    
    #génération du dataframe pour les tableaux 
    columns = ['Le nombre de Winnings Historique','Le nombre de créa', '%']
    columns2 = ['Le nombre de Winnings Historique', 'Le nombre de carte', '%']
    index = df_nbAttachments.index
    index2 = ['MUT']
    
    

    #Premier tableau (Créa et Winnings par personne)
    response = pd.DataFrame(index = index, columns = columns)
    response['Le nombre de Winnings Historique'] = df_nbAttachments
    response['Le nombre de créa'] = df_nbAttachments2
    response['%'] = response['Le nombre de Winnings Historique']/response['Le nombre de créa']*100

    #Deuxième tableau Créa et Winnings par étiquette
    response2 = pd.DataFrame(index = index2, columns = columns2 )
    response2['Le nombre de Winnings Historique'] = [trie(df_cards_members_list, data_label_selected)]
    response2['Le nombre de carte'] = [trie(df_cards_members_list_total, data_label_selected)]
    response2['%'] = response2['Le nombre de Winnings Historique']/response2['Le nombre de carte']*100

    st.markdown('## Cartes et Winnings par étiquette')
    
    st.write(response2)
    
    # tableau des Créa et Winnings par personne
    st.markdown("## Créa et Winnings par personne")
    st.write(response)
    st.markdown("Si une personne n'est pas dans le tableau alors elle n'a jamais fait de créa en Winnings Historique")

    

if option == "Formation":
    #création du dataframe des listes présentes sur le Trello
    url2 = "https://api.trello.com/1/boards/HPxeEdAB/lists?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url2)
    df_list = response.json()
    df_list = pd.json_normalize(df_list)

    
    #génération du dataframe des membres du tableau Trello
    url1 = "https://api.trello.com/1/boards/HPxeEdAB/members?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url1)
    df_members = response.json()
    df_members = pd.json_normalize(df_members)


    #génération du dataframe des cartes présentes sur le Trello
    url = "https://sirin.hipto.com/index.php/Sandbox/frederick_trello_one?bordname=buformation"
    reponse = requests.get(url)
    df_cards = reponse.json()
    df_cards = pd.json_normalize(df_cards)

    if st.sidebar.button('Afficher semaine passée'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_week = pd.to_datetime(day_last_week)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_week) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]

    if st.sidebar.button('Afficher mois passé'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_month = pd.to_datetime(day_last_month)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_month) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]
    

    #Travail sur l'id des membres du tableau
    df_cards['idMembers'] = df_cards['idMembers'].astype(str)
    df_cards['idMembers'] = df_cards['idMembers'].apply(lambda x: x.replace("['","").replace("']",''))
    df_members['id'] = df_members['id'].astype(str)

    #création d'un dataframe avec cartes et membres
    df_cards_members = pd.merge(df_members, df_cards, left_on = ['id'],right_on = ['idMembers'])
    df_cards_members_list = pd.merge(df_list,df_cards_members, left_on =['id'] ,right_on =['idList'] )
    df_cards_members_list_total = df_cards_members_list

    #création d'un tableau contenant les infos uniquement des cartes dans Winnings Historique
    df_cards_members_list_mask = df_cards_members_list['name_x'] == 'Winnings historique'
    df_cards_members_list = df_cards_members_list[df_cards_members_list_mask]

    #Génération du datfarame des labels
    url3 = "https://api.trello.com/1/boards/HPxeEdAB/labels?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url3)
    df_labels= response.json()
    df_labels = pd.json_normalize(df_labels)
    df_labels = df_labels[['id','name','color']]
    c = count_rows(df_labels)
    for i in range (0,c):
        df_labels['label_complet'] = df_labels['name'] + " " + df_labels['color']
    

    #code permettant d'avoir les labels dans la sidebar (sans les verticales)   
    labels = df_labels['label_complet']
    mask_label_complet = df_labels['label_complet'].str.contains("green")
    df_labels = df_labels[mask_label_complet == False]
    labels = df_labels['label_complet']

    #code permettant de récupérer le nombres de créa présentes sur les cartes 
    label_name(df_cards_members_list['labels'],df_cards_members_list)
    label_name(df_cards_members_list_total['labels'],df_cards_members_list_total)
    df_cards_members_list['nbCrea'] = df_cards_members_list['badges.attachments']
    df_nbAttachments = df_cards_members_list.groupby(['fullName']).sum()
    df_nbAttachments = df_nbAttachments['nbCrea']
    df_cards_members['nbCrea'] = df_cards_members['badges.attachments']
    df_nbAttachments2 = df_cards_members.groupby(['fullName']).sum()
    df_nbAttachments2 = df_nbAttachments2['nbCrea']
    
    #génération de la barre de multiselection 
    data_label_selected = st.multiselect('labels Winnings Historique',labels)
    
    #génération du dataframe pour les tableaux 
    columns = ['Le nombre de Winnings Historique','Le nombre de créa', '%']
    columns2 = ['Le nombre de Winnings Historique', 'Le nombre de carte', '%']
    index = df_nbAttachments.index
    index2 = ['MON green','PE green','SNO green']
    
    

    #Premier tableau (Créa et Winnings par personne)
    response = pd.DataFrame(index = index, columns = columns)
    response['Le nombre de Winnings Historique'] = df_nbAttachments
    response['Le nombre de créa'] = df_nbAttachments2
    response['%'] = response['Le nombre de Winnings Historique']/response['Le nombre de créa']*100

    #Deuxième tableau Créa et Winnings par étiquette
    response2 = pd.DataFrame(index = index2, columns = columns2 )
    response2['Le nombre de Winnings Historique'] = [trie(df_cards_members_list,["MON green"]+ data_label_selected), trie(df_cards_members_list,["PE green"]+ data_label_selected),trie(df_cards_members_list,["SNO green"]+ data_label_selected)]
    response2['Le nombre de carte'] = [trie(df_cards_members_list_total,["MON green"]+ data_label_selected), trie(df_cards_members_list_total,["PE green"]+ data_label_selected), trie(df_cards_members_list_total,["SNO green"]+ data_label_selected)]
    response2['%'] = response2['Le nombre de Winnings Historique']/response2['Le nombre de carte']*100


    st.markdown('## Cartes et Winnings par étiquette')
    
    st.write(response2)
    
    # tableau des Créa et Winnings par personne
    st.markdown("## Créa et Winnings par personne")
    st.write(response)
    st.markdown("Si une personne n'est pas dans le tableau alors elle n'a jamais fait de créa en Winnings Historique")

    

if option == "Assurance":
    #création du dataframe des listes présentes sur le Trello
    url2 = "https://api.trello.com/1/boards/6DwAab38/lists?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url2)
    df_list = response.json()
    df_list = pd.json_normalize(df_list)

    
    #génération du dataframe des membres du tableau Trello
    url1 = "https://api.trello.com/1/boards/6DwAab38/members?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url1)
    df_members = response.json()
    df_members = pd.json_normalize(df_members)


    #génération du dataframe des cartes présentes sur le Trello
    url = "https://sirin.hipto.com/index.php/Sandbox/frederick_trello_one?bordname=buassurance"
    reponse = requests.get(url)
    df_cards = reponse.json()
    df_cards = pd.json_normalize(df_cards)

    if st.sidebar.button('Afficher semaine passée'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_week = pd.to_datetime(day_last_week)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_week) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]

    if st.sidebar.button('Afficher mois passé'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_month = pd.to_datetime(day_last_month)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_month) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]
    

    #Travail sur l'id des membres du tableau
    df_cards['idMembers'] = df_cards['idMembers'].astype(str)
    df_cards['idMembers'] = df_cards['idMembers'].apply(lambda x: x.replace("['","").replace("']",''))
    df_members['id'] = df_members['id'].astype(str)

    #création d'un dataframe avec cartes et membres
    df_cards_members = pd.merge(df_members, df_cards, left_on = ['id'],right_on = ['idMembers'])
    df_cards_members_list = pd.merge(df_list,df_cards_members, left_on =['id'] ,right_on =['idList'] )
    df_cards_members_list_total = df_cards_members_list

    #création d'un tableau contenant les infos uniquement des cartes dans Winnings Historique
    df_cards_members_list_mask = df_cards_members_list['name_x'] == 'Winnings'
    df_cards_members_list = df_cards_members_list[df_cards_members_list_mask]

    #Génération du datfarame des labels
    url3 = "https://api.trello.com/1/boards/6DwAab38/labels?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url3)
    df_labels= response.json()
    df_labels = pd.json_normalize(df_labels)
    df_labels = df_labels[['id','name','color']]
    c = count_rows(df_labels)
    for i in range (0,c):
        df_labels['label_complet'] = df_labels['name'] + " " + df_labels['color']

    #code permettant d'avoir les labels dans la sidebar (sans les verticales)   
    labels = df_labels['label_complet']
    mask_label_complet = df_labels['label_complet'].str.contains("green")
    df_labels = df_labels[mask_label_complet == False]
    labels = df_labels['label_complet']

    #code permettant de récupérer le nombres de créa présentes sur les cartes 
    label_name(df_cards_members_list['labels'],df_cards_members_list)
    label_name(df_cards_members_list_total['labels'],df_cards_members_list_total)
    df_cards_members_list['nbCrea'] = df_cards_members_list['badges.attachments']
    df_nbAttachments = df_cards_members_list.groupby(['fullName']).sum()
    df_nbAttachments = df_nbAttachments['nbCrea']
    df_cards_members['nbCrea'] = df_cards_members['badges.attachments']
    df_nbAttachments2 = df_cards_members.groupby(['fullName']).sum()
    df_nbAttachments2 = df_nbAttachments2['nbCrea']
    
    #génération de la barre de multiselection 
    data_label_selected = st.multiselect('labels Winnings Historique',labels)
    
    #génération du dataframe pour les tableaux 
    columns = ['Le nombre de Winnings Historique','Le nombre de créa', '%']
    columns2 = ['Le nombre de Winnings Historique', 'Le nombre de carte', '%']
    index = df_nbAttachments.index
    index2 = ['ACCblg green','ACCfra green','ACCita green','ADP green','ASA green','ASE green','MUT green','OBS green']
    
    

    #Premier tableau (Créa et Winnings par personne)
    response = pd.DataFrame(index = index, columns = columns)
    response['Le nombre de Winnings Historique'] = df_nbAttachments
    response['Le nombre de créa'] = df_nbAttachments2
    response['%'] = response['Le nombre de Winnings Historique']/response['Le nombre de créa']*100

    #Deuxième tableau Créa et Winnings par étiquette
    response2 = pd.DataFrame(index = index2, columns = columns2 )
    response2['Le nombre de Winnings Historique'] = [trie(df_cards_members_list,["ACCblg green"]+ data_label_selected), trie(df_cards_members_list,["ACCfra green"]+ data_label_selected),trie(df_cards_members_list,["ACCita green"]+ data_label_selected), trie(df_cards_members_list,["ADP green"]+ data_label_selected), trie(df_cards_members_list,["ASA green"]+ data_label_selected), trie(df_cards_members_list,["ASE green"]+ data_label_selected), trie(df_cards_members_list,["MUT green"]+ data_label_selected), trie(df_cards_members_list,["OBS green"]+ data_label_selected)]
    response2['Le nombre de carte'] = [trie(df_cards_members_list_total,["ACCblg green"]+ data_label_selected), trie(df_cards_members_list_total,["ACCfra green"]+ data_label_selected), trie(df_cards_members_list_total,["ACCita green"]+ data_label_selected), trie(df_cards_members_list_total,["ADP green"]+ data_label_selected), trie(df_cards_members_list_total,["ASA green"]+ data_label_selected), trie(df_cards_members_list_total,["ASE green"]+ data_label_selected), trie(df_cards_members_list_total,["MUT green"]+ data_label_selected), trie(df_cards_members_list_total,["OBS green"]+ data_label_selected)]
    response2['%'] = response2['Le nombre de Winnings Historique']/response2['Le nombre de carte']*100

    st.markdown('## Cartes et Winnings par étiquette')
    
    st.write(response2)
    
    # tableau des Créa et Winnings par personne
    st.markdown("## Créa et Winnings par personne")
    st.write(response)
    st.markdown("Si une personne n'est pas dans le tableau alors elle n'a jamais fait de créa en Winnings Historique")

    

if option == "Travaux":
    #création du dataframe des listes présentes sur le Trello
    url2 = "https://api.trello.com/1/boards/YA5qrtq6/lists?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url2)
    df_list = response.json()
    df_list = pd.json_normalize(df_list)

    
    #génération du dataframe des membres du tableau Trello
    url1 = "https://api.trello.com/1/boards/YA5qrtq6/members?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url1)
    df_members = response.json()
    df_members = pd.json_normalize(df_members)


    #génération du dataframe des cartes présentes sur le Trello
    url = "https://sirin.hipto.com/index.php/Sandbox/frederick_trello_one?bordname=butravaux"
    reponse = requests.get(url)
    df_cards = reponse.json()
    df_cards = pd.json_normalize(df_cards)

    if st.sidebar.button('Afficher semaine passée'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_week = pd.to_datetime(day_last_week)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_week) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]

    if st.sidebar.button('Afficher mois passé'):
        df_cards['dateLastActivity'] = pd.to_datetime(df_cards['dateLastActivity']).dt.date
        day_last_month = pd.to_datetime(day_last_month)
        today = pd.to_datetime(today)
        mask_date = (df_cards['dateLastActivity']> day_last_month) & (df_cards['dateLastActivity']<today)
        df_cards = df_cards[mask_date]
    

    #Travail sur l'id des membres du tableau
    df_cards['idMembers'] = df_cards['idMembers'].astype(str)
    df_cards['idMembers'] = df_cards['idMembers'].apply(lambda x: x.replace("['","").replace("']",''))
    df_members['id'] = df_members['id'].astype(str)

    #création d'un dataframe avec cartes et membres
    df_cards_members = pd.merge(df_members, df_cards, left_on = ['id'],right_on = ['idMembers'])
    df_cards_members_list = pd.merge(df_list,df_cards_members, left_on =['id'] ,right_on =['idList'] )
    df_cards_members_list_total = df_cards_members_list

    #création d'un tableau contenant les infos uniquement des cartes dans Winnings Historique
    df_cards_members_list_mask = df_cards_members_list['name_x'] == 'Winnings historique'
    df_cards_members_list = df_cards_members_list[df_cards_members_list_mask]

    #Génération du datfarame des labels
    url3 = "https://api.trello.com/1/boards/YA5qrtq6/labels?key=f0e3de5f744267d6d4dbf82cbfe27ca6&token=6475a4b1c7a84f924026c2e91d63dc8d79895f9c807d16c1b95c7e3f06c675cc"
    response = requests.get(url3)
    df_labels= response.json()
    df_labels = pd.json_normalize(df_labels)
    df_labels = df_labels[['id','name','color']]
    c = count_rows(df_labels)
    for i in range (0,c):
        df_labels['label_complet'] = df_labels['name'] + " " + df_labels['color']

    #code permettant d'avoir les labels dans la sidebar (sans les verticales)   
    labels = df_labels['label_complet']
    mask_label_complet = df_labels['label_complet'].str.contains("green")
    df_labels = df_labels[mask_label_complet == False]
    labels = df_labels['label_complet']
    

    #code permettant de récupérer le nombres de créa présentes sur les cartes 
    label_name(df_cards_members_list['labels'],df_cards_members_list)
    label_name(df_cards_members_list_total['labels'],df_cards_members_list_total)
    df_cards_members_list['nbCrea'] = df_cards_members_list['badges.attachments']
    df_nbAttachments = df_cards_members_list.groupby(['fullName']).sum()
    df_nbAttachments = df_nbAttachments['nbCrea']
    df_cards_members['nbCrea'] = df_cards_members['badges.attachments']
    df_nbAttachments2 = df_cards_members.groupby(['fullName']).sum()
    df_nbAttachments2 = df_nbAttachments2['nbCrea']
    
    #génération de la barre de multiselection 
    data_label_selected = st.multiselect('labels Winnings Historique',labels)
    
    #génération du dataframe pour les tableaux 
    columns = ['Le nombre de Winnings Historique','Le nombre de créa', '%']
    columns2 = ['Le nombre de Winnings Historique', 'Le nombre de carte', '%']
    index = df_nbAttachments.index
    index2 = ['ADE green','CARSUN green','DP green','ME green','ME ITA green','PAC green','PAC AA green','RAD green','RECRUT green']
    
    

    #Premier tableau (Créa et Winnings par personne)
    response = pd.DataFrame(index = index, columns = columns)
    response['Le nombre de Winnings Historique'] = df_nbAttachments
    response['Le nombre de créa'] = df_nbAttachments2
    response['%'] = response['Le nombre de Winnings Historique']/response['Le nombre de créa']*100

    #Deuxième tableau Créa et Winnings par étiquette
    response2 = pd.DataFrame(index = index2, columns = columns2 )
    response2['Le nombre de Winnings Historique'] = [trie(df_cards_members_list,["ADE green "]+ data_label_selected), trie(df_cards_members_list,["CARSUN green "]+ data_label_selected),trie(df_cards_members_list,["DP green "]+ data_label_selected), trie(df_cards_members_list,["ME green "]+ data_label_selected), trie(df_cards_members_list,["PAC green "] +  data_label_selected), trie(df_cards_members_list,["PAC AA green "]+ data_label_selected), trie(df_cards_members_list,["RAD green "]+ data_label_selected), trie(df_cards_members_list,["RECRUT green "]+ data_label_selected), trie(df_cards_members_list,["ME ITA green "]+ data_label_selected)]
    response2['Le nombre de carte'] = [trie(df_cards_members_list_total,["ADE green "]+ data_label_selected), trie(df_cards_members_list_total,["CARSUN green "]+ data_label_selected), trie(df_cards_members_list_total,["DP green "]+ data_label_selected), trie(df_cards_members_list_total,["ME green "]+ data_label_selected), trie(df_cards_members_list_total,["PAC green"]+ [" "] +  data_label_selected), trie(df_cards_members_list_total,["PAC AA green "]+ data_label_selected), trie(df_cards_members_list_total,["RAD green "]+ data_label_selected), trie(df_cards_members_list_total,["RECRUT green "]+ data_label_selected), trie(df_cards_members_list_total,["ME ITA green "]+ data_label_selected)]
    response2['%'] = response2['Le nombre de Winnings Historique']/response2['Le nombre de carte']*100

    

    st.markdown('## Cartes et Winnings par étiquette')
    
    st.write(response2)
    
    # tableau des Créa et Winnings par personne
    st.markdown("## Créa et Winnings par personne")
    st.write(response)
    st.markdown("Si une personne n'est pas dans le tableau alors elle n'a jamais fait de créa en Winnings Historique")

    





    


# code faisant aparaitre les différents dataframes via une checkbox 
if st.sidebar.checkbox('Montrer les dataframes'):
    st.subheader('Raw data')
    st.write('Dataframe des listes')
    st.write(df_list)
    st.write('Dataframe des membres')
    st.write(df_members)
    st.write('Dataframe des cartes')
    st.write(df_cards)
    st.write('Datframe cartes x membres')
    st.write(df_cards_members)
    st.write('Dataframe cartes x membres x listes')
    st.write(df_cards_members_list)
    st.write('labels')
    st.write(data_label_selected)
    st.write(df_nbAttachments)
    st.write(df_cards_members_list_total)
    st.write('url')
    st.write(reponse)
    
    




