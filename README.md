# Renoveerimispakkumiste rakenduse demo

Tere!

Näitan kuidas töötab minu renoveerimispakkumiste rakendus

Rakenduse eesmärk on genereerida renoveerimispakkumine olemasolevate renoveerimispakkumiste põhjal.

Rakenduse kasutamine:
1. Kasutaja sisestab renoveeritava hoone EHR koodi.
2. Rakendus võrdleb hoonet selliste hoonetega, millele on juba olemas renoveerimispakkumine.
3. Nende hoonete seast leitakse kõige sarnasem hoone.
4. Kõige sarnasema hoone renoveerimispakkumise mahte ja hindu muudetakse vastavalt uue hoone mõõtudele.
5. Seejärel kuvatakse uus renoveerimispakkumine kasutajale.
6. Kasutaja saab liikuda ka renoveerimipakkumise juurest tagasi ning sisestada uusi hooneid.

Rakenduse äriloogika on arendatud Pythonis ja veebirakendus kasutab Flask raamisitkku. Rakenduse koodis on palju ära kasutatud  [Big Data for Digital Construction](https://github.com/innarliiv/bigdata4digitalconstruction) repositooriumi näiteid.

Vaatame nüüd kuidas rakendus töötab. Leiame pakkumised suvalistele majadele ehitisregistrist.  

*[Rakenduse demo](https://youtu.be/12dIWZ3VFvM)*

Aitäh vaatamast!

PS! Tegemist on nö prototüübiga, selles võib veel esineda vigu :)  
Vaata äriloogika seletust business_logic_explanation.md

