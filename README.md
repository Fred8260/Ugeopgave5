# PDF Download Script
Dette Python-script automatiserer download af PDF-rapporter fra links i et Excel-ark,
håndterer fejl i downloadprocessen og gemmer filerne med specifikke navne. Det logger også,
hvilke rapporter der er blevet downloadet korrekt, og hvilke der fejlede (I hver deres respektive folders).

## Beskrivelse:
Scriptet hjælper med at automatisere processen med at downloade PDF-rapporter fra links i en Excel-fil. Det bruger kolonnen `BRNummer` 
til at navngive PDF-filerne og indeholder fejlhåndtering til at prøve et alternativt link,
hvis det første mislykkes. Scriptet genererer en log over succesfulde og mislykkede downloads, hvilket giver et hurtigt overblik over resultaterne.

### Krav:
Dette script kræver følgende Python-biblioteker:

- `pandas`
- `requests`
- `PyPDF2`

#### Installation af afhængigheder
Hvis du er i tvivl om, hvordan du kan installere de nødvendige biblioteker, kan du bruge følgende kommando i IDE-terminalen:

```bash
pip install pandas requests PyPDF2
