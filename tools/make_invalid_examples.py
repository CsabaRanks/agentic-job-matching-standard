"""Regenerate examples/invalid*/ and examples/invalid/expectations.json.

Each negative example is a valid example with exactly one targeted mutation, paired with
the error it must produce (kind, JSON pointer, message fragment). Run from the repo root:

    python tools/make_invalid_examples.py
"""
import copy, json, sys
sys.path.insert(0, "src")
from ajms.validation import validate_document
C = json.load(open("examples/valid/candidate-supply-chain-analyst.full-private.json"))
J = json.load(open("examples/valid/job-demand-planner.public.json"))
N = json.load(open("examples/valid/job-icu-nurse.public.json"))
cases = {}
def case(folder, name, base, mutate, kind, path, contains, why):
    d = copy.deepcopy(base); mutate(d)
    cases[f"{folder}/{name}"] = (d, {"kind": kind, "path": path, "contains": contains, "why": why})


case("invalid","candidate-missing-schema-version.json",C,lambda d:d.pop("schemaVersion"),"schema","","'schemaVersion' is a required property","Every profile must state its schema version.")
case("invalid","candidate-compensation-without-currency.json",C,lambda d:d["jobPreferences"]["compensation"]["hardCondition"]["atLeast"].pop("currency"),"schema","/jobPreferences/compensation","closest cause at /jobPreferences/compensation/hardCondition/atLeast: 'currency' is a required property","A salary without currency is ambiguous.")
case("invalid","job-compensation-without-period.json",J,lambda d:d["offer"]["compensation"][0].pop("period"),"schema","/offer/compensation","closest cause at /offer/compensation/0: 'period' is a required property","A salary without period (hour, month, year) is ambiguous.")
case("invalid","job-estimated-salary-as-point-value.json",J,lambda d:d["offer"]["compensation"].append({"component":"TOTAL_TARGET_CASH","currency":"EUR","period":"YEAR","grossOrNet":"GROSS","value":75000,"informationKind":"ESTIMATED"}),"schema","/offer/compensation","closest cause at /offer/compensation/2: 'min' is a required property","Estimates must be stated as an interval.")
case("invalid","job-remote-share-without-reference-period.json",J,lambda d:d["offer"]["workModel"]["remoteShare"].pop("referencePeriod"),"schema","/offer/workModel","closest cause at /offer/workModel/remoteShare: 'referencePeriod' is a required property","A remote share needs its reference period (week, month, year).")
case("invalid","candidate-commute-distance-in-minutes.json",C,lambda d:d["jobPreferences"]["location"]["hardCondition"]["commute"]["maxOneWayDistance"].__setitem__("unitCode","MIN"),"schema","/jobPreferences/location","maxOneWayDistance/unitCode: 'MIN' is not one of","Distance and travel time are different quantities; MIN is not a distance unit.")
P = json.load(open("examples/valid/candidate-supply-chain-analyst.public-minimal.json"))
case("invalid","candidate-public-minimal-with-identity.json",P,lambda d:d.__setitem__("identity",{"displayName":"Jordan Example"}),"schema","","False schema does not allow this value (keys: displayName)","A public minimal representation must not carry identity data.")
case("invalid","job-domain-criterion-wrong-value-type.json",N,lambda d:d["requirements"]["domainCriteria"][0]["criterion"].__setitem__("value","yes"),"schema","/requirements/domainCriteria/0/criterion/value","is not of type 'boolean'","dataType BOOLEAN requires a boolean value.")
case("invalid","job-domain-criterion-unstable-id.json",N,lambda d:d["requirements"]["domainCriteria"][1]["criterion"].__setitem__("criterionId","Fachgebiet"),"schema","/requirements/domainCriteria/1/criterion/criterionId","does not match","Domain criteria need a stable reverse-DNS identifier.")
case("invalid","job-with-candidate-preferences.json",J,lambda d:d.__setitem__("jobPreferences",{}),"schema","","('jobPreferences' was unexpected)","A JobProfile must not carry candidate-side fields.")
case("invalid","candidate-evidenced-without-evidence-ref.json",C,lambda d:d["capabilities"]["qualifications"][0]["provenance"].pop("evidenceRefs"),"schema","/capabilities/qualifications/0/provenance","'evidenceRefs' is a required property","An evidenced statement must point to its evidence.")
case("invalid","candidate-wrong-type.json",C,lambda d:d.__setitem__("@type","Person"),"schema","/@type","missing or unknown @type","Only AJMS document types are accepted.")
case("invalid","candidate-hybrid-wish-without-wrapper.json",C,lambda d:d["jobPreferences"].__setitem__("workModel",{"arrangements":{"include":["HYBRID"]}}),"schema","/jobPreferences/workModel","('arrangements' was unexpected)","Preferences must say whether they are a hardCondition or a wish.")
case("invalid-semantic","job-salary-min-greater-than-max.json",J,lambda d:d["offer"]["compensation"][0].update({"min":80000,"max":70000}),"semantic","/offer/compensation/0","min (80000) is greater than max (70000)","Ranges must be ordered; JSON Schema cannot express this.")
case("invalid-semantic","candidate-dangling-evidence-ref.json",C,lambda d:d["capabilities"]["competencies"][2]["provenance"].__setitem__("evidenceRefs",["ev-missing"]),"semantic","/capabilities/competencies/2/provenance/evidenceRefs","evidence 'ev-missing' is not listed","Evidence references must resolve within the document.")
case("invalid-semantic","job-start-window-reversed.json",J,lambda d:d["requirements"]["startTiming"].update({"earliestStartDate":"2027-05-01"}),"semantic","/requirements/startTiming","earliestStartDate is after latestStartDate","Date windows must be ordered.")
case("invalid-semantic","candidate-ongoing-with-end-month.json",C,lambda d:d["experienceHistory"][0].__setitem__("endMonth","2025-12"),"semantic","/experienceHistory/0","an ongoing entry must not have endMonth","Contradictory employment period.")
case("invalid-semantic","candidate-duplicate-competency-id.json",C,lambda d:d["capabilities"]["competencies"][1].__setitem__("competencyId","demand-forecasting"),"semantic","/capabilities/competencies/1/competencyId","duplicate competencyId","Local identifiers must be unique.")

IMP = json.load(open("examples/adapters/job-ad-text-de/senior-demand-planner.jobprofile.json"))
N_IDX = next(i for i, st in enumerate(IMP["fieldStatements"]) if st["statementKind"] == "NORMALIZED")
case("invalid","imported-normalized-without-method.json",IMP,lambda d:d["fieldStatements"][N_IDX].pop("method"),"schema",f"/fieldStatements/{N_IDX}","'method' is a required property","A normalized value must name the rule that converted it.")
case("invalid-semantic","imported-statement-points-nowhere.json",IMP,lambda d:d["fieldStatements"][0].__setitem__("path","/offer/remoteShare"),"semantic","/fieldStatements/0/path","/offer/remoteShare does not resolve","A field statement must refer to a field that exists.")

expectations = {}
ok = True
for key,(doc,exp) in cases.items():
    errs=[i for i in validate_document(doc) if i.level=="error"]
    hit=any(i.kind==exp["kind"] and i.path==exp["path"] and exp["contains"] in i.message for i in errs)
    if not hit:
        ok=False; print("MISS",key,[str(i) for i in errs][:4])
    json.dump(doc, open("examples/"+key,"w",encoding="utf-8"), indent=2, ensure_ascii=False); open("examples/"+key,"a").write("\n")
    expectations[key]=exp
json.dump(expectations, open("examples/invalid/expectations.json","w"), indent=2, ensure_ascii=False)
open("examples/invalid/expectations.json","a").write("\n")
print("all hit" if ok else "SOME MISSED", len(cases))
sys.exit(0 if ok else 1)
