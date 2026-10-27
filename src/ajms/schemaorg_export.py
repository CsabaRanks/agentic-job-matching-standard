"""Transform a JobProfile into a schema.org JobPosting (JSON-LD).

Only for real, published vacancies (profileView PUBLIC). Candidate preferences are never
exported as JobPosting: a wish is not an advertised job. The output uses schema.org terms
only; AJMS-specific information without a schema.org equivalent is left out and listed in
docs/schema-org-mapping.md. Producing this markup does not imply eligibility for any
search engine feature.
"""

from __future__ import annotations

from . import match as _m

EMPLOYMENT_TYPE = {
    "PERMANENT_EMPLOYMENT": None,
    "FIXED_TERM_EMPLOYMENT": "TEMPORARY",
    "TEMPORARY_AGENCY_WORK": "TEMPORARY",
    "FREELANCE": "CONTRACTOR",
    "INTERNSHIP": "INTERN",
    "APPRENTICESHIP": "OTHER",
    "WORKING_STUDENT": "PART_TIME",
}


def _txt(value) -> str:
    return _m._text(value)


def _place(place: dict) -> dict:
    address = {"@type": "PostalAddress", "addressCountry": place["countryCode"]}
    for src, dst in (("region", "addressRegion"), ("locality", "addressLocality"), ("postalCode", "postalCode")):
        if src in place:
            address[dst] = place[src]
    out = {"@type": "Place", "address": address}
    if "geo" in place:
        out["geo"] = {"@type": "GeoCoordinates", "latitude": place["geo"]["latitude"], "longitude": place["geo"]["longitude"]}
    return out


def _amount(entry: dict) -> dict:
    value = {"@type": "QuantitativeValue", "unitText": entry["period"]}
    if "value" in entry:
        value["value"] = entry["value"]
    for key, dst in (("min", "minValue"), ("max", "maxValue")):
        if key in entry:
            value[dst] = entry[key]
    return {"@type": "MonetaryAmount", "currency": entry["currency"], "value": value}


def to_job_posting(job: dict) -> dict:
    if job.get("@type") != "JobProfile":
        raise ValueError("only a JobProfile can be exported as schema.org JobPosting")
    if job.get("profileView") != "PUBLIC":
        raise ValueError("only PUBLIC job profiles describe advertised vacancies")
    offer, req = job.get("offer", {}), job.get("requirements", {})
    posting: dict = {"@context": "https://schema.org", "@type": "JobPosting", "title": _txt(job["title"])}

    tasks = [_txt(t["label"]) for t in job.get("tasks", [])]
    if tasks:
        posting["responsibilities"] = "; ".join(tasks)
        posting["description"] = "<p>" + "</p><p>".join(tasks) + "</p>"
    if "datePosted" in job:
        posting["datePosted"] = job["datePosted"]
    if "validThrough" in job:
        posting["validThrough"] = job["validThrough"]
    if "postingUrl" in job:
        posting["url"] = job["postingUrl"]
    posting["identifier"] = {"@type": "PropertyValue", "propertyID": "ajms:profileId", "value": job["profileId"]}

    org = job.get("hiringOrganization", {})
    if "name" in org:
        hiring = {"@type": "Organization", "name": org["name"]}
        if "url" in org:
            hiring["sameAs"] = org["url"]
        posting["hiringOrganization"] = hiring
    industries = [f"{i['scheme']} {i['code']}" for i in org.get("industries", [])]
    if industries:
        posting["industry"] = [{"@type": "DefinedTerm", "name": code, "termCode": code.split(" ", 1)[1]} for code in industries]

    archetype = job.get("archetype", {})
    isco = [c["code"] for c in archetype.get("occupationCodes", []) if c["scheme"] == "ISCO-08"]
    if isco:
        posting["occupationalCategory"] = [{"@type": "CategoryCode", "codeValue": code, "inCodeSet": {"@type": "CategoryCodeSet", "name": "ISCO-08"}} for code in isco]

    if isinstance(offer.get("locations"), list):
        posting["jobLocation"] = [_place(p) for p in offer["locations"]]
    work_model = offer.get("workModel")
    if isinstance(work_model, dict) and work_model.get("arrangement") == "REMOTE":
        posting["jobLocationType"] = "TELECOMMUTE"
        if work_model.get("remoteCountries"):
            posting["applicantLocationRequirements"] = [{"@type": "Country", "name": c} for c in work_model["remoteCountries"]]

    employment = []
    working_time = offer.get("workingTime")
    if isinstance(working_time, dict) and "schedule" in working_time:
        employment.append(working_time["schedule"])
    contract = offer.get("contract")
    if isinstance(contract, dict) and EMPLOYMENT_TYPE.get(contract["contractType"]):
        employment.append(EMPLOYMENT_TYPE[contract["contractType"]])
    if employment:
        posting["employmentType"] = sorted(set(employment))
    if isinstance(working_time, dict) and "weeklyHours" in working_time:
        hours = working_time["weeklyHours"]
        lo, hi = hours.get("min"), hours.get("max")
        posting["workHours"] = f"{lo:g} hours per week" if lo == hi else f"{lo or '?'}-{hi or '?'} hours per week"

    compensation = offer.get("compensation")
    if isinstance(compensation, list):
        base = [e for e in compensation if e["component"] == "BASE_SALARY" and e["grossOrNet"] == "GROSS"]
        stated = [e for e in base if e["informationKind"] == "STATED"]
        estimated = [e for e in base if e["informationKind"] == "ESTIMATED"]
        if stated:
            posting["baseSalary"] = _amount(stated[0])
        if estimated:
            posting["estimatedSalary"] = _amount(estimated[0])
        variable = [e for e in compensation if e["component"] == "VARIABLE_TARGET"]
        if variable:
            posting["incentiveCompensation"] = "; ".join(
                f"variable target {e.get('value', e.get('min'))} {e['currency']} per {e['period'].lower()}" for e in variable
            )
    benefits = [_txt(b) for b in offer.get("benefits", [])]
    if benefits:
        posting["jobBenefits"] = "; ".join(benefits)

    skills = [c for c in req.get("competencies", [])]
    if skills:
        posting["skills"] = [{"@type": "DefinedTerm", "name": _txt(c["label"])} for c in skills]
    degrees = [q for q in req.get("qualifications", []) if q["qualificationType"] == "DEGREE"]
    if degrees:
        posting["educationRequirements"] = [
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree",
             **({"educationalLevel": f"EQF level {q['minimumEqfLevel']}"} if "minimumEqfLevel" in q else {})}
            for q in degrees
        ]
        if any(q.get("experienceInPlaceOfEducation") for q in degrees):
            posting["experienceInPlaceOfEducation"] = True
    months = [e["minimumMonths"] for e in req.get("domainExperience", [])]
    if "totalExperienceMonths" in req:
        months.append(req["totalExperienceMonths"]["minimumMonths"])
    if months:
        posting["experienceRequirements"] = {"@type": "OccupationalExperienceRequirements", "monthsOfExperience": max(months)}
    if "workAuthorization" in req:
        posting["eligibilityToWorkRequirement"] = "Work authorization required for: " + ", ".join(req["workAuthorization"]["countryCodes"])
    start = req.get("startTiming", {})
    if start.get("immediate"):
        posting["jobImmediateStart"] = True
    elif "earliestStartDate" in start:
        posting["jobStartDate"] = start["earliestStartDate"]
    return posting
