from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Dashboard", layout="wide")

# --- DATA LOADER ---
@st.cache_data
def load_survey_data(survey_name):
    folder_path = Path("data") / survey_name
    
    all_files = list(folder_path.glob("*.csv"))
    
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    for file in all_files:
        if os.path.getsize(file) > 0:
            try:
                df = pd.read_csv(file)
                df_list.append(df)
            except pd.errors.EmptyDataError:
                pass
    
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, ignore_index=True)
    
    return combined_df

# --- NATIVE TABS NAVIGATION ---
tab_HSC, tab_DMS, tab_OHIx, tab_Meta = st.tabs(["HSC", "DMS", "OHIx", "MetaCategories"])

# ==========================================
# HSC TAB
# ==========================================
with tab_HSC:
    st.title("Panel 1: HSC")
    df_hsc = load_survey_data("hsc")
    
    if df_hsc.empty:
        st.warning("No HSC data available.")
    else:
        with st.expander("Sample HSC Data"):
            st.dataframe(df_hsc)

        # --- 0. TRZY PYTANIA Z NAJNIŻSZĄ ŚREDNIĄ ---
        question_cols = [col for col in df_hsc.columns if '-' in col]
        lowest_3 = df_hsc[question_cols].mean().nsmallest(3)

        text_path = Path("analysis") / "file.txt"
        if text_path.exists():
            with open(text_path, "r", encoding="utf-8") as f:
                descriptions = [line.strip() for line in f.read().split('\n') if line.strip()]
        else:
            descriptions = []

        question_dict = {
            's1-1': 'Nasza firma jasno określa, w czym jest lepsza od konkurencji.',
            's1-2': 'Decyzje strategiczne opieramy na głębokim zrozumieniu naszego rynku i jego trendów.',
            's1-3': 'W pełni rozumiemy potrzeby i oczekiwania naszych kluczowych klientów.',
            's1-4': 'Nasze zasoby i kompetencje są dobrze dostosowane do obecnych wyzwań.',
            's1-5': 'Rozumiemy, jakie zmiany w otoczeniu mogą stanowić zagrożenie lub szansę dla naszego biznesu.',
            's2-1': 'Strategia naszej firmy jasno określa, gdzie chcemy rywalizować (rynki, segmenty) i jak chcemy wygrywać.',
            's2-2': 'Proces tworzenia strategii angażuje kluczowych interesariuszy i jest dobrze skoordynowany.',
            's2-3': 'Nasza strategia umożliwia elastyczne dostosowanie do zmieniających się warunków rynkowych.',
            's2-4': 'Kierujemy się długoterminową wizją, ale uwzględniamy także krótkoterminowe priorytety.',
            's2-5': 'Strategia jest spójna i konsekwentnie wdrażana w całej organizacji.',
            's3-1': 'Nasze portfolio produktów/usług jest dobrze zrównoważone między wzrostem, stabilnością i wycofywaniem.',
            's3-2': 'Inwestujemy w rozwój nowych produktów/usług, które odpowiadają na zmieniające się potrzeby klientów.',
            's3-3': 'Rozumiemy cykl życia naszych produktów/usług i zarządzamy nim w sposób świadomy.',
            's3-4': 'Regularnie analizujemy rentowność i atrakcyjność naszych produktów/usług.',
            's3-5': 'Jesteśmy w stanie szybko wycofać się z działań, które nie przynoszą oczekiwanych wyników.',
            's4-1': 'Zarządzanie w naszej firmie jest dobrze zharmonizowane z celami strategicznymi (inspiracja Karola Adamieckiego).',
            's4-2': 'Nasze procesy decyzyjne są jasne, szybkie i wspierane przez dane.',
            's4-3': 'Angażujemy wszystkich pracowników w realizację strategii, dbając o ich zrozumienie i zaangażowanie.',
            's4-4': 'Używamy odpowiednich metod zarządzania do specyfiki naszej strategii (np. planowanie, eksperymentowanie, adaptowanie).',
            's4-5': 'Wprowadzamy innowacje w zarządzaniu, aby lepiej dopasować się do zmiennych warunków rynkowych.',

        }
        st.markdown("### 📉 Pytania z najniższą średnią:")
        st.write("") 

        for i, (col_name, avg_score) in enumerate(lowest_3.items()):
            desc = descriptions[i] if i < len(descriptions) else "Brak analizy w pliku file.txt."
            question = question_dict.get(col_name, col_name)
            st.markdown(f"**„{question}”**")
            st.markdown(f"👉 Średnia: {avg_score:.2f}")
            message = st.text_input("Analiza: ", key=f"analysis_{col_name}")
            st.markdown(f"⛳ {desc}")
            st.write("") 
        
        st.divider() 

        # --- 1. RADAR I BOXPLOT ---
        categories = {
            's1': 'Metody zarządzania',
            's2': 'Portfolio produktów/usług',
            's3': 'Pozycjonowanie firmy',
            's4': 'Strategia'
        }

        for prefix, cat_name in categories.items():
            cols = [col for col in df_hsc.columns if col.startswith(prefix)]
            if cols:
                df_hsc[cat_name] = df_hsc[cols].mean(axis=1)
        
        cat_cols = list(categories.values())

        means = df_hsc[cat_cols].mean().tolist()
        mins = df_hsc[cat_cols].min().tolist()
        maxs = df_hsc[cat_cols].max().tolist()

        radar_cats = cat_cols + [cat_cols[0]]
        radar_means = means + [means[0]]
        radar_mins = mins + [mins[0]]
        radar_maxs = maxs + [maxs[0]]

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=radar_maxs, theta=radar_cats, mode='lines',
            line=dict(color='#ff4b4b', dash='dash', width=1.5), name='Maksymalna'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_mins, theta=radar_cats, mode='lines',
            line=dict(color='#ff7f0e', dash='dash', width=1.5), name='Minimalna'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_means, theta=radar_cats, fill='toself',
            fillcolor='rgba(245, 166, 35, 0.4)', 
            line=dict(color='#f5a623', width=2), name='Średnia'
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            legend=dict(yanchor="bottom", y=-0.3, xanchor="left", x=0),
            margin=dict(l=40, r=40, t=20, b=20)
        )

        df_melted = df_hsc.melt(value_vars=cat_cols, var_name='Kategoria', value_name='Ocena')

        fig_box = px.box(
            df_melted, x='Kategoria', y='Ocena', color='Kategoria',
            color_discrete_sequence=['#E39B20', '#D46A40', '#D8445F', '#DE68B5'] 
        )

        fig_box.update_layout(
            showlegend=False, 
            xaxis_title=None, 
            yaxis=dict(range=[0, 10.5]),
            margin=dict(l=20, r=20, t=20, b=20)
        )

        col_left, col_right = st.columns(2)

        with col_left:
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_right:
            st.plotly_chart(fig_box, use_container_width=True)

        # --- 2. NPS I ANALIZA ---
        def calc_nps(series):
            promoters = (series >= 9).sum()
            detractors = (series <= 6).sum()
            total = len(series)
            if total == 0: return 0
            return ((promoters - detractors) / total) * 100

        nps_data = {cat: calc_nps(df_hsc[cat]) for cat in cat_cols}
        
        df_nps = pd.DataFrame(list(nps_data.items()), columns=['Kategoria', 'NPS']).sort_values('NPS')

        color_map = {
            'Metody zarządzania': '#E39B20', 
            'Portfolio produktów/usług': '#D46A40', 
            'Pozycjonowanie firmy': '#D8445F', 
            'Strategia': '#DE68B5'
        }
        df_nps['Color'] = df_nps['Kategoria'].map(color_map)

        fig_nps = go.Figure(go.Bar(
            x=df_nps['Kategoria'],
            y=df_nps['NPS'],
            marker_color=df_nps['Color'],
            text=[f"{val:.1f}%" for val in df_nps['NPS']],
            textposition='outside'
        ))

        fig_nps.update_layout(
            title=dict(text="NPS dla każdej kategorii DMS", x=0.5),
            yaxis=dict(range=[-100, 100], title="NPS (%)", zeroline=True, zerolinecolor='black'),
            xaxis=dict(title="Kategoria"),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40)
        )

        analysis_path = Path("analysis") / "dms.txt"
        if analysis_path.exists():
            with open(analysis_path, "r", encoding="utf-8") as f:
                analysis_text = f.read()
        else:
            analysis_text = "**Brak pliku:** Utwórz plik `analysis/dms.txt`, aby wyświetlić tutaj wnioski."

        st.write("---")
        
        col_nps_left, col_text_right = st.columns([1.5, 1.0])

        with col_nps_left:
            st.plotly_chart(fig_nps, use_container_width=True)

        with col_text_right:
            st.markdown(analysis_text)

# ==========================================
# DMS TAB
# ==========================================
with tab_DMS:
    st.title("Panel 2: DMS")
    df_dms = load_survey_data("dms")
    if df_dms.empty:
        st.warning("No DMS data available.")
    else:
        with st.expander("DMS Data"):
            st.dataframe(df_dms)

        # --- 0. TRZY PYTANIA Z NAJNIŻSZĄ ŚREDNIĄ ---
        question_cols = [col for col in df_dms.columns if '-' in col]
        lowest_3 = df_dms[question_cols].mean().nsmallest(3)

        text_path = Path("analysis") / "file.txt"
        if text_path.exists():
            with open(text_path, "r", encoding="utf-8") as f:
                descriptions = [line.strip() for line in f.read().split('\n') if line.strip()]
        else:
            descriptions = []

        question_dict = {
            's1-1': 'Organizacja posiada jasno określoną strategię cyfrową zgodną z jej długoterminowymi celami biznesowymi.',
            's1-2': 'Strategia cyfrowa organizacji jest jasno i konsekwentnie komunikowana na wszystkich poziomach.',
            's1-3': 'Organizacja regularnie aktualizuje swoją strategię cyfrową, aby dostosować się do zmieniającego się rynku.',
            's1-4': 'Technologie cyfrowe są integralną częścią strategii wzrostu organizacji.',
            's1-5': 'Liderzy organizacji rozumieją wpływ technologii na konkurencyjność i innowacyjność.',
            's2-1': 'Organizacja efektywnie wykorzystuje nowoczesne technologie do usprawnienia procesów operacyjnych.',
            's2-2': 'Technologia cyfrowa jest wykorzystywana do tworzenia nowych produktów, usług lub modeli biznesowych.',
            's2-3': 'Organizacja promuje kulturę innowacyjności i eksperymentowania z nowymi technologiami.',
            's2-4': 'Wdrożone przez organizację technologie są nowoczesne i odpowiednie do realizacji jej celów biznesowych.',
            's2-5': 'Organizacja posiada proces monitorowania nowych technologii i ich wpływu na rynek.',
            's3-1': 'Organizacja posiada dobrze określoną strategię zarządzania danymi, obejmującą ich pozyskiwanie, przechowywanie, analizę i wykorzystanie.',
            's3-2': 'Dane w organizacji traktowane są jako wartościowy zasób wspierający procesy decyzyjne.',
            's3-3': 'Organizacja korzysta z zaawansowanych narzędzi analitycznych do przetwarzania danych i pozyskiwania wniosków biznesowych.',
            's3-4': 'Pracownicy mają łatwy dostęp do danych oraz narzędzi niezbędnych do podejmowania decyzji.',
            's3-5': 'Organizacja posiada skuteczne mechanizmy ochrony danych, zgodne z przepisami dotyczącymi prywatności.',
            's4-1': 'Organizacja posiada kulturę wspierającą innowacje, współpracę i dzielenie się wiedzą.',
            's4-2': 'Pracownicy są odpowiednio przeszkoleni i posiadają niezbędne kompetencje cyfrowe do wykonywania swoich zadań.',
            's4-3': 'Organizacja inwestuje w rozwój kompetencji cyfrowych swoich pracowników, wspierając transformację cyfrową.',
            's4-4': 'Kultura organizacyjna sprzyja szybkiemu wdrażaniu nowych technologii.',
            's4-5': 'Liderzy organizacji aktywnie promują wykorzystywanie technologii w codziennych działaniach.',
            's5-1': 'Organizacja posiada solidną i elastyczną infrastrukturę IT wspierającą realizację celów cyfrowych.',
            's5-2': 'Systemy informatyczne w organizacji są zintegrowane, umożliwiając płynny przepływ informacji między działami, zespołami lub funkcjami.',
            's5-3': 'Infrastruktura IT jest skalowalna, aby sprostać rosnącym potrzebom organizacji.',
            's5-4': 'Organizacja korzysta z rozwiązań IT opartym na chmurze, zwiększających elastyczność i efektywność.',
            's5-5': 'Organizacja regularnie ocenia i modernizuje swoją infrastrukturę IT, aby sprostać wymaganiom cyfrowe świata.',

        }
        st.markdown("### 📉 Pytania z najniższą średnią:")
        st.write("") 

        for i, (col_name, avg_score) in enumerate(lowest_3.items()):
            desc = descriptions[i] if i < len(descriptions) else "Brak analizy w pliku file.txt."
            question = question_dict.get(col_name, col_name)
            st.markdown(f"**„{question}”**")
            st.markdown(f"👉 Średnia: {avg_score:.2f}")
            st.markdown(f"⛳ {desc}")
            st.write("") 
        
        st.divider() 


# ==========================================
# OHIx TAB
# ==========================================
with tab_OHIx:
    st.title("Panel 3: OHIx")
    df_ohix = load_survey_data("ohix")
    if df_ohix.empty:
        st.warning("No OHIx data available.")
    else:
        with st.expander("OHIx Data"):
            st.dataframe(df_ohix)

        # --- 0. TRZY PYTANIA Z NAJNIŻSZĄ ŚREDNIĄ ---
        question_cols = [col for col in df_ohix.columns if '-' in col]
        lowest_3 = df_ohix[question_cols].mean().nsmallest(3)

        text_path = Path("analysis") / "file.txt"
        if text_path.exists():
            with open(text_path, "r", encoding="utf-8") as f:
                descriptions = [line.strip() for line in f.read().split('\n') if line.strip()]
        else:
            descriptions = []

        question_dict = {
            's1-1': 'Organizacja ma jasną i inspirującą wizję, która wyznacza kierunek strategiczny.',
            's1-2': 'Liderzy aktywnie komunikują cele i priorytety organizacji w sposób spójny i zrozumiały.',
            's1-3': 'Proces podejmowania decyzji jest transparentny i zgodny z misją oraz wartościami organizacji.',
            's1-4': 'Liderzy koncentrują się na długoterminowym sukcesie, a nie jedynie na krótkoterminowych wynikach.',
            's1-5': 'Liderzy w sposób świadomy wspierają współpracę w obszarach, które przynoszą największą wartość.',
            's2-1': 'Organizacja ma dobrze zdefiniowaną strategię, która jest spójna z wizją i wartościami.',
            's2-2': 'Zasoby są alokowane efektywnie w celu realizacji strategicznych celów.',
            's2-3': 'Współpraca pomiędzy działami jest celowa i ukierunkowana na realizację priorytetów strategicznych.',
            's2-4': 'Organizacja efektywnie dostosowuje się do zmian na rynku lub w otoczeniu biznesowym.',
            's2-5': 'W organizacji istnieje kultura wzajemnej odpowiedzialności za realizację celów i zobowiązań.',
            's3-1': 'Pracownicy czują, że ich wkład jest doceniany i ma znaczenie dla organizacji.',
            's3-2': 'Współpraca między zespołami jest zarządzana tak, aby unikać zbędnego przeciążenia.',
            's3-3': 'Konstruktywne konflikty i różnice opinii są wspierane i skutecznie zarządzane, aby osiągnąć lepsze decyzje.',
            's3-4': 'Pracownicy uważają swoją pracę za znaczącą i zgodną z celem organizacji.',
            's3-5': 'Organizacja promuje otwartą i szczerą komunikację na wszystkich poziomach.',
            's4-1': 'Organizacja inwestuje w rozwój zawodowy swoich pracowników.',
            's4-2': 'Szanuje się równowagę między życiem zawodowym a prywatnym, a pracownicy czują wsparcie w zarządzaniu obowiązkami.',
            's4-3': 'Pracownicy wszystkich poziomów angażują się w realizację wspólnych celów i działają z poczuciem misji.',
            's4-4': 'Organizacja aktywnie zbiera i wykorzystuje opinie, aby poprawić doświadczenie i efektywność pracowników.',
            's4-5': 'W organizacji panuje kultura zaufania i wzajemnego szacunku między pracownikami a kierownictwem.',
            's5-1': 'Organizacja promuje kulturę wzajemnego szacunku i współpracy, zapewniając, że każdy pracownik czuje się doceniony.',
            's5-2': 'Praktyki etyczne i integralność są głęboko zakorzenione w działaniach organizacji.',
            's5-3': 'Organizacja jest zaangażowana społecznie i odpowiedzialna wobec społeczności.',
            's5-4': 'W organizacji współpraca opiera się na dokładnie określonych celach i przynosi wymierne rezultaty.',
            's5-5': 'Organizacja konsekwentnie dąży do osiągania wspólnych wyników, wyżej ceniąc sukces zespołu niż indywidualne osiągnięcia.'

        }
        st.markdown("### 📉 Pytania z najniższą średnią:")
        st.write("") 

        for i, (col_name, avg_score) in enumerate(lowest_3.items()):
            desc = descriptions[i] if i < len(descriptions) else "Brak analizy w pliku file.txt."
            question = question_dict.get(col_name, col_name)
            st.markdown(f"**„{question}”**")
            st.markdown(f"👉 Średnia: {avg_score:.2f}")
            st.markdown(f"⛳ {desc}")
            st.write("") 
        
        st.divider() 


# ==========================================
# MetaCategories TAB
# ==========================================
with tab_Meta:
    st.title("Panel 4: Analiza Metakategorii")
    
    # --- 1. POBIERANIE I ŁĄCZENIE DANYCH Z ANKIET ---
    df_hsc = load_survey_data("hsc")
    df_dms = load_survey_data("dms")
    df_ohix = load_survey_data("ohix")
    
    if df_hsc.empty or df_dms.empty or df_ohix.empty:
        st.warning("Brakuje danych w jednym z folderów (hsc, dms, ohix), aby wygenerować analizę metakategorii.")
    else:
        min_len = min(len(df_hsc), len(df_dms), len(df_ohix))
        df_combined = pd.DataFrame()
        
        for col in df_hsc.columns:
            if '-' in col: df_combined[f"hsc_{col.replace('-', '_')}"] = df_hsc[col].iloc[:min_len]
        for col in df_dms.columns:
            if '-' in col: df_combined[f"dms_{col.replace('-', '_')}"] = df_dms[col].iloc[:min_len]
        for col in df_ohix.columns:
            if '-' in col: df_combined[f"ohix_{col.replace('-', '_')}"] = df_ohix[col].iloc[:min_len]

        # --- WZORY DLA METAKATEGORII ---
        meta_formulas = {
            'Strategia i Wizja': '0.40 * hsc_s1_1 + 0.60 * dms_s4_4',
            'Pozycjonowanie Rynkowe': '1.0 * hsc_s2_1',
            'Portfolio (Produkty/Usługi)': '1.0 * hsc_s3_1',
            'Technologia i Innowacyjność': '1.0 * dms_s2_1',
            'Dane i Analityka': '1.0 * dms_s3_1',
            'Operacje i Procesy': '1.0 * hsc_s4_2',
            'Infrastruktura i zasoby': '1.0 * dms_s5_1',
            'Ludzie i Kultura Organizacyjna': '1.0 * ohix_s4_1',
            'Harmonia i Przywództwo': '1.0 * ohix_s5_5'
        }

        # --- 2. OBLICZANIE STATYSTYK DO TABELI I WYKRESU ---
        stats_list = []
        
        dummy_min_df = pd.DataFrame(1, index=[0], columns=df_combined.columns)
        dummy_max_df = pd.DataFrame(10, index=[0], columns=df_combined.columns)

        for cat_name, formula in meta_formulas.items():
            try:
                real_scores = df_combined.eval(formula)
                
                # Teoretyczne min/max dla szarego tła
                theo_min = dummy_min_df.eval(formula).iloc[0]
                theo_max = dummy_max_df.eval(formula).iloc[0]
                
                stats_list.append({
                    'Kategoria': cat_name,
                    'Theo Min': theo_min,
                    'Wartość minimalna': real_scores.min(),
                    'Q1': real_scores.quantile(0.25),
                    'Mediana': real_scores.median(),
                    'Średnia': real_scores.mean(),
                    'Q3': real_scores.quantile(0.75),
                    'Wartość maksymalna': real_scores.max(),
                    'Theo Max': theo_max
                })
            except Exception as e:
                st.error(f"Sprawdź wzór dla '{cat_name}'. Błąd: {e}")
                
        df_stats = pd.DataFrame(stats_list)

        # --- 3. TWORZENIE WYKRESU ---
        fig_meta = go.Figure()
        categories = df_stats['Kategoria'][::-1]

        for index, row in df_stats[::-1].iterrows():
            # 1. Szare tło: Teoretyczne MIN do Teoretyczne MAX
            fig_meta.add_trace(go.Scatter(
                x=[row['Theo Min'], row['Theo Max']],
                y=[row['Kategoria'], row['Kategoria']],
                mode='lines',
                line=dict(color='#E0E0E0', width=20),
                hoverinfo='text',
                hovertext=f"Zakres teoretyczny: {row['Theo Min']:.1f} - {row['Theo Max']:.1f}"
            ))
            
            # 2. Czarna "świeca": Realne MIN do Realne MAX
            fig_meta.add_trace(go.Scatter(
                x=[row['Wartość minimalna'], row['Wartość maksymalna']],
                y=[row['Kategoria'], row['Kategoria']],
                mode='lines',
                line=dict(color='black', width=4),
                hoverinfo='text',
                hovertext=f"Realny rozrzut z ankiet: {row['Wartość minimalna']:.1f} - {row['Wartość maksymalna']:.1f}"
            ))
            
            # 3. Niebieska kropka - Średnia
            fig_meta.add_trace(go.Scatter(
                x=[row['Średnia']],
                y=[row['Kategoria']],
                mode='markers+text',
                marker=dict(color='blue', size=8),
                text=[f"{row['Średnia']:.1f}"],
                textposition='bottom center',
                textfont=dict(color='blue', size=10)
            ))

        fig_meta.update_layout(
            showlegend=False,
            height=500,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='lightgray', showline=True, linecolor='black'),
            yaxis=dict(gridcolor='lightgray'),
            plot_bgcolor='white'
        )

        # --- 4. WYŚWIETLANIE NA DASHBOARDZIE ---
        col_text, col_chart = st.columns([1, 2])

        with col_text:
            st.markdown("### 🔍 Co możemy wyczytać z tego wykresu?")
            st.markdown("""
            **Rozrzut wyników:**
            Niektóre metakategorie, jak np. "Strategia i Wizja" czy "Harmonia i Przywództwo", wykazują znaczną rozpiętość między respondentami – to sugeruje brak spójnego doświadczenia w organizacji.
            
            Inne, jak np. "Dane i Analityka", są bardziej spójne, ale niższe mediany mogą być sygnałem do poprawy.

            **Pozycja średniej (środkowa kropka):**
            Pokazuje ogólny poziom dojrzałości w danym obszarze. Niskie średnie przy dużej zmienności wskazują na brak jednolitych standardów.

            **Długość świecy (czarna linia):**
            Długie świece = organizacja działa nierównomiernie w danym obszarze. Jedne zespoły mają dobre praktyki, inne niemal ich nie mają. To sygnał do integracji i standaryzacji.
            """)

        with col_chart:
            st.plotly_chart(fig_meta, use_container_width=True)
            display_cols = ['Kategoria', 'Wartość minimalna', 'Q1', 'Mediana', 'Średnia', 'Q3', 'Wartość maksymalna']
            df_stats_display = df_stats[display_cols].set_index('Kategoria').round(2)
            st.dataframe(df_stats_display, use_container_width=True)