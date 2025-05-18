
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Utleieinvestering Kalkulator", layout="wide")
st.markdown("<h1 style='color:#2E86C1;'>Utleieinvestering Kalkulator</h1>", unsafe_allow_html=True)

# Tilbakestill og default-knapper
col1, col2 = st.sidebar.columns(2)

if col1.button("Reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if col2.button("Default"):
    st.session_state["kjøpesum"] = 3000000.0
    st.session_state["laan"] = 2850000.0
    st.session_state["rente"] = 5.6
    st.session_state["leie"] = 25000.0
    st.session_state["kostnader"] = 30000.0
    st.session_state["vekst"] = 1.0
    st.session_state["oppussing_bad"] = 200000.0
    st.session_state["oppussing_kjokken"] = 150000.0
    st.session_state["oppussing_gulv"] = 100000.0
    st.session_state["oppussing_annet"] = 50000.0
    st.session_state["faktor_bad"] = 2.5
    st.session_state["faktor_kjokken"] = 2.0
    st.session_state["faktor_gulv"] = 1.5
    st.session_state["faktor_annet"] = 1.0
    st.rerun()

# Verdiøkning prosent
verdiokning_input = st.number_input("Årlig verdistigning (%)", min_value=0.0, step=0.1, format="%.2f")
verdiøkning = verdiokning_input / 100

eierform = st.sidebar.radio("Eierform", ["Privat", "AS"])

finn_link = st.sidebar.text_input("Lenke til Finn-annonsen (valgfritt)", placeholder="https://www.finn.no/...")

# Inndata
st.sidebar.markdown("### Grunnleggende investering")
with st.sidebar.expander("Grunnleggende investering", expanded=True):
    kjøpesum = st.number_input("Kjøpesum", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["kjøpesum"] if "kjøpesum" in st.session_state else 0.0, key="kjøpesum", placeholder="f.eks. 3000000")
    laan = st.number_input("Lånebeløp", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["laan"] if "laan" in st.session_state else 0.0, key="laan", placeholder="f.eks. 2850000")
    rente = st.number_input("Rente (%)", min_value=0.0, step=0.1, format="%.2f", value=st.session_state["rente"] if "rente" in st.session_state else 0.0, key="rente", placeholder="f.eks. 5.6") / 100
    leie = st.number_input("Leie per måned", min_value=0.0, step=500.0, format="%.0f", value=st.session_state["leie"] if "leie" in st.session_state else 0.0, key="leie", placeholder="f.eks. 25000")
    kostnader = st.number_input("Årlige driftskostnader", min_value=0.0, step=1000.0, format="%.0f", value=st.session_state["kostnader"] if "kostnader" in st.session_state else 0.0, key="kostnader", placeholder="f.eks. 30000")
    vekst = st.number_input("Årlig leie-/kostnadsvekst (%)", min_value=0.0, step=0.1, format="%.2f", value=st.session_state["vekst"] if "vekst" in st.session_state else 0.0, key="vekst", placeholder="f.eks. 1") / 100
antall_år = st.sidebar.slider("Antall år for simulering", 1, 10, value=5)

# Oppussing per rom

with st.sidebar.expander("Oppussing", expanded=False):
    oppussing_bad = st.number_input("Bad", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["oppussing_bad"] if "oppussing_bad" in st.session_state else 0.0, key="oppussing_bad", placeholder="f.eks. 200000")
    oppussing_kjokken = st.number_input("Kjøkken", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["oppussing_kjokken"] if "oppussing_kjokken" in st.session_state else 0.0, key="oppussing_kjokken", placeholder="f.eks. 150000")
    oppussing_gulv = st.number_input("Gulv/overflater", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["oppussing_gulv"] if "oppussing_gulv" in st.session_state else 0.0, key="oppussing_gulv", placeholder="f.eks. 100000")
    oppussing_annet = st.number_input("Annet", min_value=0.0, step=10000.0, format="%.0f", value=st.session_state["oppussing_annet"] if "oppussing_annet" in st.session_state else 0.0, key="oppussing_annet", placeholder="f.eks. 50000")
    oppussing = oppussing_bad + oppussing_kjokken + oppussing_gulv + oppussing_annet

# Verdiøkning per rom
with st.sidebar.expander("Verdiøkning per romtype", expanded=False):
    faktor_bad = st.number_input("Multiplikator bad", min_value=0.0, step=0.1, format="%.2f", key="faktor_bad")
    faktor_kjokken = st.number_input("Multiplikator kjøkken", min_value=0.0, step=0.1, format="%.2f", key="faktor_kjokken")
    faktor_gulv = st.number_input("Multiplikator gulv/overflater", min_value=0.0, step=0.1, format="%.2f", key="faktor_gulv")
    faktor_annet = st.number_input("Multiplikator annet", min_value=0.0, step=0.1, format="%.2f", key="faktor_annet")

# Simulering
inv_total = kjøpesum + oppussing
egenkapital = inv_total - laan
år = list(range(1, antall_år + 1))
boligverdi = kjøpesum
akkum_netto = 0
sim = []

for i in år:
    leie_aar = leie * 12 * ((1 + vekst) ** (i - 1))
    renter_total = laan * rente
    kost_aar = kostnader * ((1 + vekst) ** (i - 1))
    netto = leie_aar - renter_total - kost_aar
    skatt = netto * 0.22 if netto > 0 else 0
    netto_etter_skatt = netto - skatt
    if i == 1:
        boligverdi += (
            oppussing_bad * faktor_bad +
            oppussing_kjokken * faktor_kjokken +
            oppussing_gulv * faktor_gulv +
            oppussing_annet * faktor_annet
        )
    else:
        boligverdi *= (1 + verdiøkning)
    akkum_netto += netto_etter_skatt
    sim.append({
        "År": i,
        "Leieinntekter": round(leie_aar),
        "Renter": round(renter_total),
        "Kostnader": round(kost_aar),
        "Netto før skatt": round(netto),
        "Skatt (22%)": round(skatt),
        "Netto etter skatt": round(netto_etter_skatt),
        "Boligverdi": round(boligverdi),
        "Akkumulert netto": round(akkum_netto)
    })

df = pd.DataFrame(sim)

# Yield og cashflow
renter_mnd = laan * rente / 12
kost_mnd = kostnader / 12
netto_mnd = leie - renter_mnd - kost_mnd
skatt_mnd = netto_mnd * 0.22
netto_cashflow = netto_mnd - skatt_mnd
brutto_yield = (leie * 12) / inv_total * 100 if inv_total else 0
netto_yield = (netto_cashflow * 12) / inv_total * 100 if inv_total else 0
egenkapital_yield = (netto_cashflow * 12) / egenkapital * 100 if egenkapital else 0

st.markdown("### Resultater")
st.dataframe(df, use_container_width=True)
st.markdown("### Yield og kontantstrøm")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Netto månedlig cashflow", f"{round(netto_cashflow):,} kr")
col2.metric("Brutto yield", f"{brutto_yield:.2f} %")
col3.metric("Netto yield", f"{netto_yield:.2f} %")
col4.metric("Yield på egenkapital", f"{egenkapital_yield:.2f} %")



import matplotlib.pyplot as plt


import matplotlib.pyplot as plt

st.markdown("### Verdiutvikling over tid")

# Juster månedlig netto for AS
if eierform == "AS":
    utbytteskatt = netto_cashflow * 0.22
    netto_cashflow_as = netto_cashflow - utbytteskatt
else:
    utbytteskatt = 0
    netto_cashflow_as = netto_cashflow

st.markdown("### Kontantstrøm og skatt")
col1, col2 = st.columns(2)
col1.metric("Månedlig netto cashflow", f"{round(netto_cashflow):,} kr")
col2.metric("Etter skatt (AS)", f"{round(netto_cashflow_as):,} kr" if eierform == "AS" else "-")




# Toggle for grafer
vis_grafer = st.checkbox("Vis grafer", value=False)
if vis_grafer:
    st.markdown("### Verdiutvikling over tid")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(df["År"], df["Boligverdi"], marker='o')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_title("Boligverdi")
    ax.set_xlabel("År")
    ax.set_ylabel("Verdi (kr)")
    st.pyplot(fig)

    st.markdown("### Leie og kontantstrøm")
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    cashflow_liste = [leie * 12 - laan * rente - kostnader for _ in år]
    leie_liste = [leie * 12 * ((1 + vekst) ** (i - 1)) for i in år]
    ax2.plot(år, leie_liste, label="Leieinntekter (årlig)")
    ax2.plot(år, [cf - cf * 0.22 if eierform == "AS" else cf for cf in cashflow_liste], label="Cashflow etter skatt")
    ax2.set_xlabel("År")
    ax2.set_ylabel("Kroner")
    ax2.set_title("Leie vs. cashflow")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig2)


# Sammenlign Privat vs AS (kun total etter skatt på cashflow og gevinst)
gevinst = boligverdi - kjøpesum - oppussing
gevinst_skatt_privat = gevinst * 0.22
gevinst_skatt_as = gevinst * 0.22 + (akkum_netto * 0.22)
netto_salg = boligverdi - gevinst_skatt_privat
netto_salg_as = boligverdi - gevinst_skatt_as

st.markdown("### Sammenligning Privat vs AS")
colp, colas = st.columns(2)
colp.metric("Privat: Netto salg etter skatt", f"{round(netto_salg):,} kr")
colas.metric("AS: Netto salg + utbytteskatt", f"{round(netto_salg_as):,} kr")


# Anbefaling basert på høyest nettoresultat
if netto_salg_as > netto_salg:
    st.success("Anbefaling: Det lønner seg å eie gjennom AS basert på simuleringen.")
elif netto_salg_as < netto_salg:
    st.success("Anbefaling: Det lønner seg å eie som privatperson basert på simuleringen.")
else:
    st.info("Begge eierformer gir tilnærmet likt resultat.")

if finn_link:
    st.markdown(f"### Lenke til annonse")
    st.markdown(f"[Åpne Finn-annonse]({finn_link})", unsafe_allow_html=True)
