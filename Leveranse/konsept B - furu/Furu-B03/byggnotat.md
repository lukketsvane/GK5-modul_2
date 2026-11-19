# Byggnotat B03

- Makroen frå Astra stoppa i FreeCAD 1.0 fordi `Part.Compound` manglar `CenterOfMass`. Retta med hjelpefunksjonen `com()`, som reknar massesenteret frå dei enkelte solidane. Tre kall er bytte. Elles er makroen uendra.
