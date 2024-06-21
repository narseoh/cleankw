import streamlit as st
import pandas as pd
import unidecode
from io import BytesIO

# Fonction pour nettoyer les mots clés
def clean_keywords(df, mots_inutiles):
    if 'mots clés' not in df.columns:
        st.error("Le fichier Excel doit contenir une colonne nommée 'mots clés'.")
        return df

    df['mots clés modifiés'] = ''
    for index, row in df.iterrows():
        mots_cles = str(row['mots clés'])
        
        # Utiliser unidecode pour translittérer les caractères accentués
        mots_cles = unidecode.unidecode(mots_cles)
        
        # Remplacer les apostrophes courantes dans les mots
        mots_cles = mots_cles.replace("d'", "").replace("l'", "")
        
        # Supprimer les caractères non alphanumériques
        mots_cles = ''.join(c if c.isalnum() else ' ' for c in mots_cles)
        
        # Supprimer les mots inutiles
        mots_cles = ' '.join([mot for mot in mots_cles.split() if mot.lower() not in mots_inutiles])
        
        # Supprimer les occurrences de "l " au début des mots clés
        if mots_cles.startswith("l "):
            mots_cles = mots_cles[2:]
        
        # Remplacer les " l " au milieu des chaînes par un espace
        mots_cles = mots_cles.replace(" l ", " ")

        df.at[index, 'mots clés modifiés'] = mots_cles

    if 'VRM' in df.columns:
        df['VRM max'] = df.groupby('mots clés modifiés')['VRM'].transform('max')
        df['VRM total'] = df.groupby('mots clés modifiés')['VRM'].transform('sum')

    return df

# Interface Streamlit
st.title("Keyword List Cleaner")

# Liste des mots inutiles par défaut
mots_inutiles_defaut = ['un', 'une', 'de', 'du', 'des', 'la', 'le', 'les', 'à', ' a ', 'au', 'aux', 'et', 'en']

# Zone de texte pour permettre à l'utilisateur de voir et de modifier les mots inutiles par défaut
mots_inutiles_texte = st.text_area(
    "Mots inutiles (séparés par des virgules)",
    value=", ".join(mots_inutiles_defaut)
)

# Conversion de la chaîne de caractères en liste, en supprimant les espaces inutiles et en mettant les mots en minuscule
mots_inutiles = [mot.strip().lower() for mot in mots_inutiles_texte.split(',')]

uploaded_file = st.file_uploader("Téléchargez un fichier Excel avec une colonne 'mots clés'", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu des données téléchargées :")
        st.write(df)

        if st.button("Nettoyer les mots clés"):
            df_cleaned = clean_keywords(df, mots_inutiles)

            st.write("Mots inutiles pris en compte :")
            st.write(mots_inutiles)

            st.write("Données nettoyées :")
            st.write(df_cleaned)

            # Affichage des mots clés les plus fréquents
            mots_freq = df_cleaned['mots clés modifiés'].value_counts()
            st.write("Mots clés les plus fréquents :")
            st.write(mots_freq)

            # Préparation du fichier pour le téléchargement
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df_cleaned.to_excel(writer, index=False, sheet_name='Feuille1')
            writer.close()
            processed_data = output.getvalue()

            st.download_button(
                label="Télécharger les données nettoyées",
                data=processed_data,
                file_name='nom_du_fichier_modifie.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
