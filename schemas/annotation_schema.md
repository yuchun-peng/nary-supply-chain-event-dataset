# Annotation Schema

This document describes the event and entity type definitions used in the **N-ary Supply Chain Event Dataset**. The complete annotation schema comprises **31 event categories** and **15 entity types**.

## Event Type Definitions

The dataset includes 30 named event categories and an additional `Other` category.

| Event Type | Definition | Possible Relations |
| --- | --- | --- |
| Procurement | The subject obtains, purchases, or sources products, components, raw materials, energy, equipment, or services from an external party, with explicit procurement or acquisition semantics. | buy, purchase, procure, source, obtain, acquire from |
| Raw_Material_Use | The company uses, consumes, relies on, or incorporates specific raw materials, minerals, chemicals, or energy inputs in its products, processes, or operations. This does not necessarily imply a procurement activity. | use, utilize, consume, rely on, require, contain, incorporate |
| Manufacturing | The subject manufactures, processes, assembles, fabricates, refines, or otherwise physically transforms products, components, or materials, with emphasis on the manufacturing or transformation process. | manufacture, assemble, fabricate, process, refine, retread, make |
| Production | Describes what is produced, production volume or capacity, production status, or changes in production level or timing, with emphasis on output, scale, and production status. | produce, begin production, start production, increase production, reduce production, ramp up, ramp down |
| Supply | The subject supplies, delivers, ships, or distributes physical products, components, materials, or equipment to another party, with emphasis on the physical flow of goods. | supply, deliver, ship, distribute, provide |
| Sales | The subject sells, markets, or commercially offers products to customers or markets. | sell, market, commercialize, offer for sale |
| Service_Provision | The subject provides or performs non-physical services such as maintenance, installation, charging, warranty, technical support, software access, or other services. | provide, service, repair, install, support, maintain, operate, offer |
| Product_Portfolio | Describes the products, product lines, or product categories currently offered, produced, sold, or provided by the company. | include, consist of, offer, products include, portfolio includes |
| Technology_Use | The company uses, adopts, deploys, integrates, owns, or possesses a specific technology, software, platform, system, or technological capability. | use, utilize, employ, deploy, adopt, own, possess, integrate, incorporate |
| Development | The subject researches, designs, develops, engineers, tests, creates, or improves products, technologies, platforms, systems, or processes. | develop, design, engineer, research, test, improve, create, advance |
| Product_Launch | The subject launches, introduces, releases, or begins commercial offering of a new product or service. | launch, introduce, release, debut, begin offering |
| Discontinuation | The subject permanently or indefinitely stops, withdraws, exits, or phases out a product, service, business, activity, production, or sales operation. | discontinue, cease, phase out, withdraw, exit, no longer produce, no longer sell, no longer offer |
| Infrastructure_Development | The subject constructs, establishes, opens, expands, converts, upgrades, or relocates physical facilities or operational infrastructure. | construct, build, establish, open, expand, convert, upgrade, relocate |
| Investment | The subject commits capital, assets, or other resources to a company, facility, technology, project, or other investment target. | invest, spend, commit capital, fund, contribute capital |
| Collaboration | Two or more organizations cooperate or jointly conduct research, development, manufacturing, technology, operational, or other business activities without necessarily forming a separate legal entity. | collaborate, partner, jointly develop, cooperate, work with |
| Joint_Venture | Two or more entities establish, enter into, participate in, or operate through a jointly owned business entity or venture. | form, establish, create, enter into, participate in, operate through |
| Acquisition | The subject obtains ownership or control of a company, business, major asset, technology, brand, or equity interest. | acquire, take over, purchase, buy, obtain control of |
| Divestiture | The subject sells, disposes of, separates, spins off, or otherwise relinquishes ownership of a company, business, major asset, or equity interest. | divest, dispose of, sell, sell a stake, spin off, carve out |
| Agreement | The subject enters into, signs, executes, amends, extends, renews, or terminates a formal contract, license, supply agreement, or other contractual arrangement. | enter into, sign, execute, amend, extend, renew, terminate |
| Financing | The subject obtains, provides, or arranges loans, credit, leases, bonds, notes, or other debt financing. | borrow, lend, finance, issue debt, issue notes, provide credit, lease |
| Segment_Operations | Describes the company’s existing operating segments, business divisions, or business units used to organize or report its operations. | operate, have, consist of, report as |
| Geographic_Operations | Describes the company’s existing operations, presence, or facilities in specific countries, regions, or geographic areas. | operate in, maintain, be located in, have operations in |
| Corporate_Formation | A new company, subsidiary, legal entity, or other formal organization is formed or established. | form, establish, incorporate, found, create |
| Corporate_Restructuring | An existing company undergoes a merger, reorganization, consolidation, renaming, or other organizational restructuring. | merge, reorganize, restructure, consolidate, rename |
| Regulatory_Event | A law, regulation, standard, government agency, or regulator imposes, approves, certifies, investigates, enforces, restricts, fines, or otherwise takes formal regulatory action affecting an entity. | require, mandate, impose, prohibit, restrict, regulate, approve, certify, investigate, enforce, fine, adopt, promulgate, settle |
| Workforce | Describes employment, hiring, recruitment, layoffs, workforce reductions, training, employee scale, union representation, or other workforce-related activities or conditions. | employ, hire, recruit, lay off, reduce workforce, train, represent |
| Competition | Describes explicit competition with other companies, products, or technologies, including competitors, competitive pressure, or competitive relationships. | compete with, face competition, compete for, compete against |
| Operational_Impact | An event or condition has already occurred or is occurring and has an actual effect on operations, supply, production, sales, costs, product availability, or other business activities. | affect, disrupt, delay, constrain, limit, cause, increase costs, reduce production, reduce availability, result in, lead to |
| Risk | An event, condition, or external factor has not necessarily caused an actual impact but may, could, or is expected to adversely affect operations, supply, production, sales, costs, product availability, or other business activities. | may affect, could affect, may disrupt, could result in, could lead to, could increase costs, may reduce, could adversely impact |
| Seasonality | Describes recurring seasonal or cyclical patterns in demand, sales, production, or operations. | fluctuate, peak, decline, increase, vary, seasonally higher, seasonally lower |
| Other | Any event that cannot be reasonably classified into the categories above. | — |

*The listed relations are illustrative examples rather than an exhaustive set of permitted relation expressions.*

## Entity Type Definitions

The schema defines 15 entity types used to classify the subject and object arguments of annotated events.

| Entity Type | Definition | Examples |
| --- | --- | --- |
| ORG | The filing company of the current SEC / 10-K document. | Tesla (in Tesla 10-K), Ford (in Ford 10-K), General Motors (in GM 10-K) |
| COMP | Any external company or formal organization mentioned in the filing, including competitors, suppliers, customers, partners, government agencies, regulators, labor unions, and associations. | Ford (in Tesla 10-K), EPA, UAW, European Union |
| PERSON | A named individual or a clearly identified role-based person participating in an event. | Mary Barra, CEO, Chief Financial Officer |
| PRODUCT | A product, component, equipment, or other commercialized good that a company manufactures, sells, supplies, purchases, or provides. | Model Y, tires, rearview mirrors, battery cells |
| TECHNOLOGY | A technology, software, platform, algorithm, technical system, or technological capability owned, used, adopted, deployed, or developed by a company. | ADAS, battery management system, autonomous-driving software |
| MATERIAL | A raw material, mineral, energy source, chemical, or other material input used in production, manufacturing, or operations. | steel, aluminum, lithium, rubber, natural gas |
| FACILITY | A physical operational or infrastructure site, including factories, manufacturing plants, R&D centers, warehouses, mines, offices, or charging infrastructure. | AMP-1, Normal plant, Gigafactory Texas, charging stalls |
| LOCATION | A country, state, province, city, region, or other explicit geographic location. | United States, China, Europe, Ohio |
| SEGMENT | A formally disclosed operating segment, business division, or business unit of a company. | Americas, Seating, E-Systems |
| REGULATION | A law, regulation, policy, regulatory rule, formal standard, permit, certification, or other institutional requirement. | GDPR, Clean Air Act, ISO 14001, ZEV regulations |
| AGREEMENT | A contract, agreement, license, lease, credit agreement, supply agreement, or other formal contractual document. | supply agreement, licensing agreement, credit agreement |
| IMPACT_EVENT | An event, condition, or external disruption that serves as a cause, trigger, or source of impact for another event. | semiconductor shortage, labor strike, cyberattack, natural disaster |
| METRIC_VALUE | A monetary amount, quantity, percentage, ratio, capacity, employee count, or other quantitative value. | $188 million, 15%, 39,600 employees, 150,000 units per year |
| TIME | An explicit date, year, quarter, period, time range, or other temporal expression. | 2025, Q4 2025, March 2026, through 2030 |
| OTHER | Any entity that cannot be reasonably classified into the categories above. | — |
