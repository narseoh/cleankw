import streamlit as st
import pandas as pd
import unidecode
from io import BytesIO

# Fonction pour nettoyer les mots clés
def clean_keywords(df):
    if 'mots clés' not in df.columns:
        st.error("Le fichier Excel doit contenir une colonne nommée 'mots clés'.")
        return df

    df['mots clés modifiés'] = ''
    mots_inutiles = ['un', 'une', 'de', 'du', 'des', 'la', 'le', 'les', 'à', ' a ', 'au', 'aux', 'et', 'en']

    for index, row in df.iterrows():
        mots_cles = str(row['mots clés'])
        mots_cles = mots_cles.replace("d'", "").replace("l'", "")
        mots_cles = unidecode.unidecode(mots_cles)
        mots_cles = ''.join(c if c.isalnum() else ' ' for c in mots_cles)
        mots_cles = ' '.join([mot for mot in mots_cles.split() if mot.lower() not in mots_inutiles])
        mots_cles = mots_cles.replace(" d ", " ").replace(" l ", " ")
        df.at[index, 'mots clés modifiés'] = mots_cles

    if 'VRM' in df.columns:
        df['VRM max'] = df.groupby('mots clés modifiés')['VRM'].transform('max')
        df['VRM total'] = df.groupby('mots clés modifiés')['VRM'].transform('sum')

    return df

# Interface Streamlit
st.title("Keyword List Cleaner")

uploaded_file = st.file_uploader("Téléchargez un fichier Excel avec une colonne 'mots clés'", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu des données téléchargées :")
        st.write(df)

        if st.button("Nettoyer les mots clés"):
            df_cleaned = clean_keywords(df)
            st.write("Données nettoyées :")
            st.write(df_cleaned)

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
