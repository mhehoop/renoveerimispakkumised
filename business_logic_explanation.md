## Äriloogika seletus

#### 1. Kuidas leitakse renoveeritavale hoonele kõige sarnasem pakkumine?

Leitakse renoveeritava hoone eukleidiline kaugused kõikidest olemasolevate pakkumistega hoonetest. Valitakse kõige
lähema hoone hinnapakkumine.  
Atribuudid, mida kasutatakse eukleidilise kauguse leidmiseks:

+ Hoone pindala
+ Particles arv hoone 3D joonises
+ Hoone pikkus, kõrgus, laius
+ Hoone ruumala

#### 2. Kuidas muudetakse olemasolevat pakkumist nii, et see vastaks uuele renoveeritavale hoonele?

Olemasolev pakkumine skaleeritakse tulevikus renoveeritava hoone jaoks nii, et arvutatakse renoveeritava hoone ja
olemasoelva pakkumisega hoone pindalade suhe. Seejärel korrutatakse suhtarvuga läbi kõik olemasolevad atribuudid, mis on
seotud ruumala või pindalaga (mille ühik on m2 või m3). Selle põhjal arvutatakse välja uued tööde maksumused. Loogika
on see, et arveread, mis ei ole ruumalaga seotud, neid läheb iga hoone jaoks sama palju vaja. Nt mingi masina rent
maksab erinevate hoonete puhul sama palju. Samas arveread, mis sõltuvad hoone mõõtmetest muutuvad, kuid töö ühikhind
jääb samaks, seega saab vastavalt uuele suurusele leida ligikaudse uue hinna.

#### Kui soovid rakendust oma arvutis kasutada tuleb koodis ära muuta failide asukohad!!!