# Labeling Rules

Every complaint gets exactly ONE department and ONE urgency label.
Both of us must follow these rules. If a case is not covered, discuss it, then add a rule here.

## Departments

| Label | Covers | Example |
|---|---|---|
| electricity | power cuts, live wires, transformers, streetlights, meter/billing issues | "Gali ki streetlight 5 din se band hai" |
| water_sewage | no water supply, dirty water, pipe leaks, drain/sewer overflow, waterlogging | "Nali overflow ho rahi hai, ghar mein ganda paani aa raha" |
| roads | potholes, broken roads, footpaths, illegal speed breakers | "Main road pe bada gaddha hai, bike gir gayi" |
| garbage | uncollected waste, overflowing dustbins, dead animals on road | "3 din se kachra nahi uthaya" |
| police | theft, fights, harassment, noise/crime, suspicious activity | "Raat ko gali mein chori hui" |
| health | hospital/dispensary issues, mosquito/dengue, disease outbreak, medicine shortage | "PHC mein doctor nahi aate" |
| pension_govt | pension, ration card, certificates, delays in sarkari work | "Vridha pension 4 mahine se nahi aayi" |
| other | anything else, or unclear | "Awara kutte bahut hain" |

## Rule 1: Primary issue decides the department
If a complaint mentions two issues, label the one the citizen mainly wants fixed. If it is unclear, pick the one with the higher safety risk.
- "Gali mein paani bhara hai aur bijli ka taar gira hai" -> electricity (live wire in water is the danger)
- "Road pe gaddhe hain aur unme paani bhara rehta hai" -> roads (the potholes are the root problem)

## Rule 2: Boundary cases
- Streetlight not working -> electricity (NOT roads)
- Sewage/drain overflow -> water_sewage (NOT garbage)
- Mosquitoes because of stagnant water: if the citizen complains about the drain -> water_sewage; if about dengue/fogging -> health
- Dead animal on road -> garbage
- Stray dogs -> other

## Urgency

| Label | Rule | Example |
|---|---|---|
| high | Danger to life/safety, OR essential service (power/water) fully out for 24+ hours, OR sewage entering homes, OR crime happening now | "Khula taar gira hai, bachche paas khelte hain" |
| medium | Daily life disrupted but no immediate danger | "Kal se paani nahi aa raha" |
| low | Minor inconvenience, request, or status enquiry | "Ek streetlight thodi dim hai" |

## Rule 3: Judge urgency by FACTS, not tone
CAPS, "!!!", "please jaldi" and angry language do NOT make a complaint high. Look at what is actually happening.
- "BIJLI NAHI AA RAHI!!! KOI SUNTA NAHI" (cut for 1 hour) -> medium, not high

## Rule 4: Label what is written, not what you imagine
Do not assume extra facts. If the text does not say how long the power has been out, do not label it high because it "might be" long.

## Rule 5: Potholes
- Pothole reported with no accident or blockage mentioned -> low
- Pothole causing traffic jams or damage to vehicles -> medium
- Pothole where someone has been injured, or on a very busy road at night -> high
- Vehicles or people reported slipping/falling repeatedly because of the pothole -> high

## Rule 6: Delays in government work (pension, ration card, certificates)
- Pending less than 1 month, or a simple status enquiry -> low
- Pending 1 to 3 months -> medium
- Pending more than 3 months, or the citizen depends on it for income (pension) -> high

## Rule 7: Mosquito and vector-borne disease
- Mosquito or stagnant water complaint, no illness mentioned -> health, medium
- Dengue/malaria RISK mentioned but nobody is reported sick -> medium
- People in the area reported sick, or an outbreak -> high
- Use water_sewage only if the citizen's main ask is to clear a drain or sewer

## Rule 8: Crimes (police)
- Crime against a person (assault, molestation or harassment of women, threat to life, kidnapping, acid attack, shooting, domestic violence with fear for life) -> police, high, even if it already happened
- Armed threat or crime happening right now -> police, high
- Property crime that already happened and nobody is hurt (theft, chain snatching, burglary) -> police, medium
- Noise: repeated nightly/daily -> medium; one-time, or no duration mentioned -> low

## Rule 9: Not a civic issue
- Personal or family disputes (marriage, money between people) -> other, low
- A request for a missing basic facility (e.g. village has no toilet) -> other, low

## Rules 10-15 (added 15 Oct 2026 while building the final splits; reviewed by Nimitt Malhotra)
These cover cases that came up in the real and own complaints and were not covered above.

## Rule 10: Streetlights
- One light off for 1-3 days, or a light that is dim or blinking -> electricity, low
- Off for 4+ days, several lights out, or the area is described as dark/unsafe -> medium
- Someone fell or got hurt in the dark, or the pole is sparking -> high

## Rule 11: Bills, meters and utility paperwork
- Electricity bill, meter, recharge or NOC -> electricity. Water/sewerage bill or water consumer number -> water_sewage.
- Property tax, municipal fees, refunds and wrong payments to the municipality -> pension_govt
- A bill dispute alone -> low. With a disconnection notice, or overbilling for several months -> medium.

## Rule 12: Encroachment and obstruction
- Footpath taken over (shops, carts, lawns) -> roads, low
- Road or lane space taken (walls, sheds, parked cars, illegal parking) -> other, low
- If the obstruction stops ambulances or school vans from entering -> medium
- An illegal speed breaker is always roads (see the department table)

## Rule 13: Animals (stray dogs, monkeys, cattle) -> other
- A bite or attack is reported -> high
- Chasing, aggressive animals, animals entering homes, or blocking traffic/a street -> medium
- Barking every night that stops people sleeping -> medium (same as Rule 8 noise)
- Animals present, dung, or occasional barking -> low

## Rule 14: Lost items, FIRs and illegal activity
- Item lost (not stolen) -> police, low
- Status enquiry about an earlier complaint -> police, low
- Police not acting on a real crime -> label the crime itself with Rule 8
- Ongoing illegal activity with no direct victim (drugs, gambling, illegal liquor, suspicious people at night) -> police, medium

## Rule 15: Pension dependency and hospital staff
- "Depends on it for income" in Rule 6 applies only when the text says so (no other income, household runs on it, needs it for food or medicine). Otherwise use the pending duration.
- Rude staff only -> health, low
- Care refused or delayed for a patient in a serious condition -> health, high
- Sexual misconduct by hospital staff -> police, high (Rule 8)
