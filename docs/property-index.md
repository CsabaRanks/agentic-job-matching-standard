# Property index (generated)

Generated from `schemas/v0.1/*.schema.json` by `python -m ajms build-examples`. Do not edit by hand.
The curated explanation of criteria, units and unknown-semantics is in [field-catalog.md](field-catalog.md).

## `candidate-profile.schema.json`

<a id="candidate-profile-root"></a>
### AJMS CandidateProfile v0.1

A candidate's profile: capabilities (facts and self-reports with provenance), job preferences (hard conditions separated from wishes) and availability. Contains no weights and no match results. Community Draft - not an adopted standard.

| Property | Required | Type | Description |
|---|---|---|---|
| `@context` | yes | [JsonLdContext](#common-jsonldcontext) |  |
| `@type` | yes | const `CandidateProfile` |  |
| `profileId` | yes | [ProfileId](#common-profileid) |  |
| `schemaVersion` | yes | [SchemaVersion](#common-schemaversion) |  |
| `updatedAt` | yes | [DateTime](#common-datetime) |  |
| `profileView` | yes | enum: `FULL_PRIVATE`, `SHARED_VIEW`, `PUBLIC_MINIMAL` | FULL_PRIVATE: owner's complete profile. SHARED_VIEW: a selection shared with a named recipient. PUBLIC_MINIMAL: optional coarse public representation without identity. |
| `defaultLanguage` |  | [LanguageCode](#common-languagecode) |  |
| `identity` |  | [Identity](#candidate-profile-identity) |  |
| `headline` |  | [Text](#common-text) |  |
| `summary` |  | [Text](#common-text) |  |
| `capabilities` |  | [Capabilities](#candidate-profile-capabilities) |  |
| `experienceHistory` |  | array of [ExperienceEntry](#candidate-profile-experienceentry) |  |
| `evidence` |  | array of [Evidence](#common-evidence) |  |
| `jobPreferences` |  | [JobPreferences](#candidate-profile-jobpreferences) |  |
| `availability` |  | [StartTiming](#common-starttiming) |  |
| `searchStatus` |  | enum: `ACTIVELY_SEEKING`, `OPEN_TO_OFFERS`, `NOT_SEEKING` |  |
| `source` |  | [SourceRecord](#common-sourcerecord) | For imported candidate profiles: source reference, retrieval date, format, extraction quality, unmapped content. |
| `fieldStatements` |  | array of [FieldStatement](#common-fieldstatement) | For imported candidate profiles: per-field statement kind (explicit, normalized, derived) and loss of meaning. |

<a id="candidate-profile-identity"></a>
### Identity

Directly identifying data. Belongs in FULL_PRIVATE; in a SHARED_VIEW only after the candidate decided to disclose it.

| Property | Required | Type | Description |
|---|---|---|---|
| `displayName` | yes | string (minLength 1) |  |
| `contactPoints` |  | array of object |  |
| `residence` |  | [Place](#common-place) |  |

<a id="candidate-profile-capabilities"></a>
### Capabilities

What the candidate brings. Every item may carry provenance (self-reported vs. evidenced).

| Property | Required | Type | Description |
|---|---|---|---|
| `currentCareerLevel` |  | [CareerLevel](#common-careerlevel) |  |
| `archetypes` |  | array of [JobArchetype](#common-jobarchetype) | Job archetypes the candidate has practised. |
| `competencies` |  | array of [Competency](#common-competency) |  |
| `languages` |  | array of [LanguageSkill](#common-languageskill) |  |
| `qualifications` |  | array of [Qualification](#common-qualification) |  |
| `domainExperience` |  | array of [DomainExperience](#common-domainexperience) |  |
| `totalExperienceMonths` |  | integer (minimum 0) |  |
| `leadershipExperience` |  | [Leadership](#common-leadership) |  |
| `workAuthorizations` |  | array of [WorkAuthorization](#common-workauthorization) |  |
| `domainCriteria` |  | array of [DomainCriterion](#common-domaincriterion) | Domain-specific facts about the candidate (comparator not used). |

<a id="candidate-profile-experienceentry"></a>
### ExperienceEntry

| Property | Required | Type | Description |
|---|---|---|---|
| `experienceId` | yes | [Identifier](#common-identifier) |  |
| `roleTitle` | yes | [Text](#common-text) |  |
| `organization` |  | [Organization](#common-organization) |  |
| `archetype` |  | [JobArchetype](#common-jobarchetype) |  |
| `careerLevel` |  | [CareerLevel](#common-careerlevel) |  |
| `leadership` |  | [Leadership](#common-leadership) |  |
| `startMonth` | yes | [YearMonth](#common-yearmonth) |  |
| `endMonth` |  | [YearMonth](#common-yearmonth) |  |
| `ongoing` |  | boolean |  |
| `tasks` |  | array of [Task](#common-task) |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="candidate-profile-archetypeset"></a>
### ArchetypeSet

| Property | Required | Type | Description |
|---|---|---|---|
| `include` |  | array of [JobArchetype](#common-jobarchetype) |  |
| `exclude` |  | array of [JobArchetype](#common-jobarchetype) |  |

<a id="candidate-profile-careerlevelset"></a>
### CareerLevelSet

| Property | Required | Type | Description |
|---|---|---|---|
| `include` |  | array of [CareerLevel](#common-careerlevel) |  |
| `exclude` |  | array of [CareerLevel](#common-careerlevel) |  |

<a id="candidate-profile-industryset"></a>
### IndustrySet

| Property | Required | Type | Description |
|---|---|---|---|
| `include` |  | array of [ClassificationCode](#common-classificationcode) |  |
| `exclude` |  | array of [ClassificationCode](#common-classificationcode) |  |

<a id="candidate-profile-taskset"></a>
### TaskSet

| Property | Required | Type | Description |
|---|---|---|---|
| `include` |  | array of [Task](#common-task) |  |
| `exclude` |  | array of [Task](#common-task) |  |

<a id="candidate-profile-organizationconstraint"></a>
### OrganizationConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `organizationTypes` |  | object |  |
| `sizeClasses` |  | object |  |

<a id="candidate-profile-compensationconstraint"></a>
### CompensationConstraint

atLeast: the job's figure for the same component must reach this amount.

| Property | Required | Type | Description |
|---|---|---|---|
| `atLeast` | yes | [CompensationAmount](#common-compensationamount) |  |

<a id="candidate-profile-locationconstraint"></a>
### LocationConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `commute` |  | [CommuteConditions](#common-commuteconditions) |  |
| `places` |  | array of [Place](#common-place) |  |

<a id="candidate-profile-workmodelconstraint"></a>
### WorkModelConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `arrangements` |  | object |  |
| `remoteShareAtLeast` |  | [ShareThreshold](#candidate-profile-sharethreshold) |  |
| `travelShareAtMost` |  | [ShareThreshold](#candidate-profile-sharethreshold) |  |

<a id="candidate-profile-sharethreshold"></a>
### ShareThreshold

A single percentage threshold with its reference period.

| Property | Required | Type | Description |
|---|---|---|---|
| `percent` | yes | number (minimum 0; maximum 100) |  |
| `referencePeriod` | yes | [ReferencePeriod](#common-referenceperiod) |  |

<a id="candidate-profile-workingtimeconstraint"></a>
### WorkingTimeConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `schedules` |  | object |  |
| `weeklyHours` |  | [NumberRange](#common-numberrange) |  |
| `shiftWorkAcceptable` |  | boolean |  |
| `onCallDutyAcceptable` |  | boolean |  |

<a id="candidate-profile-contractconstraint"></a>
### ContractConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `contractTypes` |  | object |  |
| `fixedTermMonthsAtLeast` |  | number (exclusiveMinimum 0) |  |

<a id="candidate-profile-developmentconstraint"></a>
### DevelopmentConstraint

| Property | Required | Type | Description |
|---|---|---|---|
| `paths` | yes | object |  |

<a id="candidate-profile-domaincriterioncondition"></a>
### DomainCriterionCondition

A domain criterion used as a condition: comparator is required.

Type: any

<a id="candidate-profile-archetypepreference"></a>
### ArchetypePreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-careerlevelpreference"></a>
### CareerLevelPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-industrypreference"></a>
### IndustryPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-organizationpreference"></a>
### OrganizationPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-taskpreference"></a>
### TaskPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-compensationpreference"></a>
### CompensationPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-locationpreference"></a>
### LocationPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-workmodelpreference"></a>
### WorkModelPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-workingtimepreference"></a>
### WorkingTimePreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-contractpreference"></a>
### ContractPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-developmentpreference"></a>
### DevelopmentPreference

Type: object or [StatedAbsence](#common-statedabsence)

<a id="candidate-profile-domaincriteriapreference"></a>
### DomainCriteriaPreference

| Property | Required | Type | Description |
|---|---|---|---|
| `hardCondition` |  | array of [DomainCriterionCondition](#candidate-profile-domaincriterioncondition) |  |
| `wish` |  | array of [DomainCriterionCondition](#candidate-profile-domaincriterioncondition) |  |

<a id="candidate-profile-jobpreferences"></a>
### JobPreferences

What the candidate looks for. hardCondition: a job outside it is not acceptable. wish: desired, not decisive. An omitted block is UNKNOWN; StatedAbsence marks NOT_APPLICABLE or NOT_DISCLOSED.

| Property | Required | Type | Description |
|---|---|---|---|
| `archetypes` |  | [ArchetypePreference](#candidate-profile-archetypepreference) |  |
| `careerLevel` |  | [CareerLevelPreference](#candidate-profile-careerlevelpreference) |  |
| `industries` |  | [IndustryPreference](#candidate-profile-industrypreference) |  |
| `organization` |  | [OrganizationPreference](#candidate-profile-organizationpreference) |  |
| `tasks` |  | [TaskPreference](#candidate-profile-taskpreference) |  |
| `compensation` |  | [CompensationPreference](#candidate-profile-compensationpreference) |  |
| `location` |  | [LocationPreference](#candidate-profile-locationpreference) |  |
| `workModel` |  | [WorkModelPreference](#candidate-profile-workmodelpreference) |  |
| `workingTime` |  | [WorkingTimePreference](#candidate-profile-workingtimepreference) |  |
| `contract` |  | [ContractPreference](#candidate-profile-contractpreference) |  |
| `development` |  | [DevelopmentPreference](#candidate-profile-developmentpreference) |  |
| `domainCriteria` |  | [DomainCriteriaPreference](#candidate-profile-domaincriteriapreference) |  |

## `job-profile.schema.json`

<a id="job-profile-root"></a>
### AJMS JobProfile v0.1

A job: what it requires from a candidate (requirements, input to Hiring-Fit) and what it offers (offer, input to Career-Fit). Uses the same shared definitions as CandidateProfile. Community Draft - not an adopted standard.

| Property | Required | Type | Description |
|---|---|---|---|
| `@context` | yes | [JsonLdContext](#common-jsonldcontext) |  |
| `@type` | yes | const `JobProfile` |  |
| `profileId` | yes | [ProfileId](#common-profileid) |  |
| `schemaVersion` | yes | [SchemaVersion](#common-schemaversion) |  |
| `updatedAt` | yes | [DateTime](#common-datetime) |  |
| `profileView` | yes | enum: `PUBLIC`, `SHARED_VIEW`, `FULL_PRIVATE` | PUBLIC: a published vacancy. SHARED_VIEW: shared with selected candidates or agents (e.g. confidential search). FULL_PRIVATE: internal working version. |
| `defaultLanguage` |  | [LanguageCode](#common-languagecode) |  |
| `title` | yes | [Text](#common-text) |  |
| `hiringOrganization` |  | [Organization](#common-organization) |  |
| `intermediary` |  | [Organization](#common-organization) | Staffing agency or recruitment consultancy publishing on behalf of the hiring organization. |
| `archetype` |  | [JobArchetype](#common-jobarchetype) |  |
| `careerLevel` |  | [CareerLevel](#common-careerlevel) |  |
| `leadership` |  | [Leadership](#common-leadership) |  |
| `tasks` |  | array of [Task](#common-task) |  |
| `requirements` |  | [Requirements](#job-profile-requirements) |  |
| `offer` |  | [Offer](#job-profile-offer) |  |
| `datePosted` |  | [Date](#common-date) |  |
| `validThrough` |  | [Date](#common-date) |  |
| `postingUrl` |  | [Uri](#common-uri) |  |
| `provenance` |  | [Provenance](#common-provenance) | Who stated the job data: ORGANIZATION_STATED for employer-published data, DERIVED for data extracted by a third party or agent. |
| `source` |  | [SourceRecord](#common-sourcerecord) | For imported job profiles: source reference, retrieval date and digest of the original text. |
| `fieldStatements` |  | array of [FieldStatement](#common-fieldstatement) | For imported job profiles: per-field statement kind (explicit, normalized, derived). |

<a id="job-profile-competencyrequirement"></a>
### CompetencyRequirement

| Property | Required | Type | Description |
|---|---|---|---|
| `competencyId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `code` |  | [ClassificationCode](#common-classificationcode) |  |
| `minimumProficiency` |  | [Proficiency](#common-proficiency) |  |
| `minimumYearsOfPractice` |  | number (minimum 0) |  |
| `requirementLevel` | yes | [RequirementLevel](#common-requirementlevel) |  |

<a id="job-profile-languagerequirement"></a>
### LanguageRequirement

| Property | Required | Type | Description |
|---|---|---|---|
| `languageCode` | yes | [LanguageCode](#common-languagecode) |  |
| `minimumCefrLevel` | yes | [CefrLevel](#common-cefrlevel) |  |
| `requirementLevel` | yes | [RequirementLevel](#common-requirementlevel) |  |

<a id="job-profile-qualificationrequirement"></a>
### QualificationRequirement

| Property | Required | Type | Description |
|---|---|---|---|
| `requirementId` | yes | [Identifier](#common-identifier) |  |
| `qualificationType` | yes | [QualificationType](#common-qualificationtype) |  |
| `label` | yes | [Text](#common-text) |  |
| `minimumEqfLevel` |  | integer (minimum 1; maximum 8) |  |
| `fieldsOfStudy` |  | array of [Text](#common-text) |  |
| `experienceInPlaceOfEducation` |  | boolean |  |
| `requirementLevel` | yes | [RequirementLevel](#common-requirementlevel) |  |

<a id="job-profile-experiencerequirement"></a>
### ExperienceRequirement

| Property | Required | Type | Description |
|---|---|---|---|
| `domainId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `code` |  | [ClassificationCode](#common-classificationcode) |  |
| `minimumMonths` | yes | integer (minimum 0) |  |
| `requirementLevel` | yes | [RequirementLevel](#common-requirementlevel) |  |

<a id="job-profile-domainrequiremententry"></a>
### DomainRequirementEntry

| Property | Required | Type | Description |
|---|---|---|---|
| `criterion` | yes | any |  |
| `requirementLevel` | yes | [RequirementLevel](#common-requirementlevel) |  |

<a id="job-profile-requirements"></a>
### Requirements

What the job requires from a candidate. REQUIRED items are hard requirements; PREFERRED items are desirable.

| Property | Required | Type | Description |
|---|---|---|---|
| `competencies` |  | array of [CompetencyRequirement](#job-profile-competencyrequirement) |  |
| `languages` |  | array of [LanguageRequirement](#job-profile-languagerequirement) |  |
| `qualifications` |  | array of [QualificationRequirement](#job-profile-qualificationrequirement) |  |
| `domainExperience` |  | array of [ExperienceRequirement](#job-profile-experiencerequirement) |  |
| `totalExperienceMonths` |  | object |  |
| `leadershipExperience` |  | object |  |
| `workAuthorization` |  | object |  |
| `startTiming` |  | [StartTiming](#common-starttiming) | When the job must be filled. Compared with the candidate's availability. |
| `domainCriteria` |  | array of [DomainRequirementEntry](#job-profile-domainrequiremententry) |  |

<a id="job-profile-offer"></a>
### Offer

What the job offers. An omitted block is UNKNOWN; StatedAbsence marks NOT_APPLICABLE or NOT_DISCLOSED (e.g. salary on request).

| Property | Required | Type | Description |
|---|---|---|---|
| `compensation` |  | array of [CompensationAmount](#common-compensationamount) or [StatedAbsence](#common-statedabsence) |  |
| `locations` |  | array of [Place](#common-place) or [StatedAbsence](#common-statedabsence) |  |
| `workModel` |  | [WorkModel](#common-workmodel) or [StatedAbsence](#common-statedabsence) |  |
| `workingTime` |  | [WorkingTime](#common-workingtime) or [StatedAbsence](#common-statedabsence) |  |
| `contract` |  | [Contract](#common-contract) or [StatedAbsence](#common-statedabsence) |  |
| `development` |  | [Development](#common-development) or [StatedAbsence](#common-statedabsence) |  |
| `benefits` |  | array of [Text](#common-text) |  |
| `domainCriteria` |  | array of [DomainCriterion](#common-domaincriterion) | Domain-specific facts about the job (comparator not used). |

## `common.schema.json`

<a id="common-schemaversion"></a>
### SchemaVersion

AJMS specification version the document claims to conform to.

Type: const `0.1.0`

<a id="common-contexturl"></a>
### ContextUrl

Type: const `https://csabaranks.github.io/agentic-job-matching-standard/context/v0.1/ajms.context.jsonld`

<a id="common-jsonldcontext"></a>
### JsonLdContext

Either the AJMS context URL or an array that contains it (additional contexts may follow).

Type: [ContextUrl](#common-contexturl) or array of any

<a id="common-profileid"></a>
### ProfileId

Stable, globally unique identifier of a profile. Either a UUID URN or an https URI. Must not encode personal data.

Type: string (pattern `^(urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\|https://[^\s]+)$`)

<a id="common-identifier"></a>
### Identifier

Local identifier, unique within one document.

Type: string (pattern `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`)

<a id="common-date"></a>
### Date

Type: string (pattern `^[0-9]{4}-(0[1-9]\|1[0-2])-(0[1-9]\|[12][0-9]\|3[01])$`)

<a id="common-yearmonth"></a>
### YearMonth

Type: string (pattern `^[0-9]{4}-(0[1-9]\|1[0-2])$`)

<a id="common-datetime"></a>
### DateTime

RFC 3339 date-time with explicit offset.

Type: string (pattern `^[0-9]{4}-(0[1-9]\|1[0-2])-(0[1-9]\|[12][0-9]\|3[01])T([01][0-9]\|2[0-3]):[0-5][0-9](:[0-5][0-9](\.[0-9]+)?)?(Z\|[+-]([01][0-9]\|2[0-3]):[0-5][0-9])$`)

<a id="common-uri"></a>
### Uri

Type: string (pattern `^(https?\|urn\|did):[^\s]+$`)

<a id="common-languagecode"></a>
### LanguageCode

BCP 47 language tag, restricted to language and optional region (e.g. de, en, de-AT).

Type: string (pattern `^[a-z]{2,3}(-[A-Z]{2})?$`)

<a id="common-countrycode"></a>
### CountryCode

ISO 3166-1 alpha-2 country code.

Type: string (pattern `^[A-Z]{2}$`)

<a id="common-currencycode"></a>
### CurrencyCode

ISO 4217 alphabetic currency code.

Type: string (pattern `^[A-Z]{3}$`)

<a id="common-text"></a>
### Text

Free text with its language. Translations are separate renderings and never replace the original.

| Property | Required | Type | Description |
|---|---|---|---|
| `text` | yes | string (minLength 1) |  |
| `language` | yes | [LanguageCode](#common-languagecode) |  |

<a id="common-statedabsence"></a>
### StatedAbsence

Explicit statement that a criterion block has no value. NOT_APPLICABLE: the criterion does not apply. NOT_DISCLOSED: a value exists but is deliberately withheld. Omitting the block entirely means UNKNOWN.

| Property | Required | Type | Description |
|---|---|---|---|
| `state` | yes | enum: `NOT_APPLICABLE`, `NOT_DISCLOSED` |  |
| `note` |  | string |  |

<a id="common-classificationcode"></a>
### ClassificationCode

A code from a named classification (occupation, industry, skill, education level). CUSTOM requires schemeUri.

| Property | Required | Type | Description |
|---|---|---|---|
| `scheme` | yes | enum: `ISCO-08`, `ESCO`, `KLDB-2010`, `ONET-SOC`, `NACE-REV2`, `WZ-2008`, `ISIC-REV4`, `NAICS`, `ISCED-2011`, `EQF`, `CUSTOM` |  |
| `code` | yes | string (minLength 1) |  |
| `uri` |  | [Uri](#common-uri) |  |
| `schemeUri` |  | [Uri](#common-uri) |  |
| `label` |  | [Text](#common-text) |  |

<a id="common-provenance"></a>
### Provenance

Where a statement comes from. Separates self-reports from evidenced statements. AJMS records evidence references; it does not verify them.

| Property | Required | Type | Description |
|---|---|---|---|
| `basis` | yes | enum: `SELF_REPORTED`, `DOCUMENT_EVIDENCED`, `THIRD_PARTY_CONFIRMED`, `ORGANIZATION_STATED`, `ESTIMATED`, `DERIVED` |  |
| `evidenceRefs` |  | array of [Identifier](#common-identifier) |  |
| `sourceUrl` |  | [Uri](#common-uri) |  |
| `assertedOn` |  | [Date](#common-date) |  |
| `note` |  | string |  |

<a id="common-evidence"></a>
### Evidence

A reference to supporting material (certificate, reference letter, credential). verificationStatus states whether anyone outside the profile owner has checked it.

| Property | Required | Type | Description |
|---|---|---|---|
| `evidenceId` | yes | [Identifier](#common-identifier) |  |
| `evidenceKind` | yes | enum: `DEGREE_CERTIFICATE`, `CERTIFICATION`, `LICENSE`, `EMPLOYMENT_REFERENCE`, `WORK_SAMPLE`, `PUBLIC_RECORD`, `VERIFIABLE_CREDENTIAL`, `OTHER` |  |
| `label` | yes | [Text](#common-text) |  |
| `issuerName` |  | string |  |
| `issuedOn` |  | [Date](#common-date) |  |
| `validUntil` |  | [Date](#common-date) |  |
| `documentUrl` |  | [Uri](#common-uri) |  |
| `verificationStatus` | yes | enum: `UNVERIFIED`, `VERIFIED_BY_THIRD_PARTY` |  |
| `verifiedBy` |  | string |  |
| `verifiedOn` |  | [Date](#common-date) |  |

<a id="common-numberrange"></a>
### NumberRange

Closed interval. One bound may be omitted (open-ended). min <= max is checked semantically.

| Property | Required | Type | Description |
|---|---|---|---|
| `min` |  | number (minimum 0) |  |
| `max` |  | number (minimum 0) |  |

<a id="common-percentrange"></a>
### PercentRange

| Property | Required | Type | Description |
|---|---|---|---|
| `min` |  | number (minimum 0; maximum 100) |  |
| `max` |  | number (minimum 0; maximum 100) |  |

<a id="common-referenceperiod"></a>
### ReferencePeriod

Period a share or count refers to.

Type: enum: `WEEK`, `MONTH`, `YEAR`

<a id="common-shareoftime"></a>
### ShareOfTime

Share of contractual working time, in percent, averaged over referencePeriod.

| Property | Required | Type | Description |
|---|---|---|---|
| `percent` | yes | [PercentRange](#common-percentrange) |  |
| `referencePeriod` | yes | [ReferencePeriod](#common-referenceperiod) |  |

<a id="common-dayscount"></a>
### DaysCount

Number of days (e.g. on-site days) within referencePeriod.

| Property | Required | Type | Description |
|---|---|---|---|
| `days` | yes | [NumberRange](#common-numberrange) |  |
| `referencePeriod` | yes | [ReferencePeriod](#common-referenceperiod) |  |

<a id="common-compensationamount"></a>
### CompensationAmount

Exactly one compensation figure: one component, one currency, one period, gross or net. Variable pay is never folded into base pay. Estimates must be intervals.

| Property | Required | Type | Description |
|---|---|---|---|
| `component` | yes | enum: `BASE_SALARY`, `VARIABLE_TARGET`, `TOTAL_TARGET_CASH`, `ALLOWANCE`, `EQUITY_TARGET`, `OTHER` |  |
| `currency` | yes | [CurrencyCode](#common-currencycode) |  |
| `period` | yes | enum: `HOUR`, `DAY`, `WEEK`, `MONTH`, `YEAR` |  |
| `grossOrNet` | yes | enum: `GROSS`, `NET` |  |
| `value` |  | number (minimum 0) |  |
| `min` |  | number (minimum 0) |  |
| `max` |  | number (minimum 0) |  |
| `hoursPerWeekBasis` |  | number (exclusiveMinimum 0; maximum 80) | Contractual weekly hours the figure refers to. Absent means the hours basis is unknown. |
| `paymentsPerYear` |  | integer (minimum 1; maximum 24) | Number of payments per year for MONTH figures (e.g. 12, 13, 14). Absent means unknown. |
| `informationKind` | yes | enum: `STATED`, `ESTIMATED` |  |
| `provenance` |  | [Provenance](#common-provenance) |  |
| `note` |  | string |  |

<a id="common-distance"></a>
### Distance

A distance. unitCode is UN/CEFACT Common Code: KMT kilometre, SMI statute mile. measurement says how it is measured.

| Property | Required | Type | Description |
|---|---|---|---|
| `value` | yes | number (minimum 0) |  |
| `unitCode` | yes | enum: `KMT`, `SMI` |  |
| `measurement` | yes | enum: `STRAIGHT_LINE`, `ROUTE` |  |

<a id="common-duration"></a>
### Duration

A duration. unitCode is UN/CEFACT Common Code: MIN minute, HUR hour.

| Property | Required | Type | Description |
|---|---|---|---|
| `value` | yes | number (minimum 0) |  |
| `unitCode` | yes | enum: `MIN`, `HUR` |  |

<a id="common-geopoint"></a>
### GeoPoint

Coordinates. precisionKm states how coarse the point deliberately is (e.g. 10 for a regional centroid).

| Property | Required | Type | Description |
|---|---|---|---|
| `latitude` | yes | number (minimum -90; maximum 90) |  |
| `longitude` | yes | number (minimum -180; maximum 180) |  |
| `precisionKm` | yes | number (minimum 0) |  |

<a id="common-place"></a>
### Place

| Property | Required | Type | Description |
|---|---|---|---|
| `countryCode` | yes | [CountryCode](#common-countrycode) |  |
| `region` |  | string |  |
| `locality` |  | string |  |
| `postalCode` |  | string |  |
| `geo` |  | [GeoPoint](#common-geopoint) |  |

<a id="common-commuteconditions"></a>
### CommuteConditions

Commute limits from an origin. Distance and travel time are separate limits; either may be given.

| Property | Required | Type | Description |
|---|---|---|---|
| `origin` | yes | [Place](#common-place) |  |
| `maxOneWayDistance` |  | [Distance](#common-distance) |  |
| `maxOneWayDuration` |  | [Duration](#common-duration) |  |
| `transportModes` |  | array of enum: `CAR`, `PUBLIC_TRANSPORT`, `BICYCLE`, `WALK` |  |
| `relocationPossible` |  | boolean |  |

<a id="common-workarrangement"></a>
### WorkArrangement

Type: enum: `ONSITE`, `HYBRID`, `REMOTE`

<a id="common-workmodel"></a>
### WorkModel

Where work happens. remoteShare and onsiteDays carry their reference period. HYBRID without remoteShare or onsiteDays leaves the share UNKNOWN.

| Property | Required | Type | Description |
|---|---|---|---|
| `arrangement` | yes | [WorkArrangement](#common-workarrangement) |  |
| `remoteShare` |  | [ShareOfTime](#common-shareoftime) |  |
| `onsiteDays` |  | [DaysCount](#common-dayscount) |  |
| `travelShare` |  | [ShareOfTime](#common-shareoftime) |  |
| `remoteCountries` |  | array of [CountryCode](#common-countrycode) |  |

<a id="common-schedule"></a>
### Schedule

Type: enum: `FULL_TIME`, `PART_TIME`

<a id="common-workingtime"></a>
### WorkingTime

Contractual working time. weeklyHours is in hours per week.

| Property | Required | Type | Description |
|---|---|---|---|
| `schedule` |  | [Schedule](#common-schedule) |  |
| `weeklyHours` |  | [NumberRange](#common-numberrange) |  |
| `shiftWork` |  | boolean |  |
| `onCallDuty` |  | boolean |  |
| `flexibleHours` |  | boolean |  |

<a id="common-contracttype"></a>
### ContractType

Type: enum: `PERMANENT_EMPLOYMENT`, `FIXED_TERM_EMPLOYMENT`, `TEMPORARY_AGENCY_WORK`, `FREELANCE`, `INTERNSHIP`, `APPRENTICESHIP`, `WORKING_STUDENT`

<a id="common-contract"></a>
### Contract

| Property | Required | Type | Description |
|---|---|---|---|
| `contractType` | yes | [ContractType](#common-contracttype) |  |
| `fixedTermMonths` |  | number (exclusiveMinimum 0) |  |
| `permanentConversionPossible` |  | boolean |  |
| `probationMonths` |  | number (minimum 0) |  |

<a id="common-careerlevel"></a>
### CareerLevel

Ordered career levels: ENTRY < JUNIOR < PROFESSIONAL < SENIOR < LEAD < HEAD < DIRECTOR < EXECUTIVE.

Type: enum: `ENTRY`, `JUNIOR`, `PROFESSIONAL`, `SENIOR`, `LEAD`, `HEAD`, `DIRECTOR`, `EXECUTIVE`

<a id="common-leadership"></a>
### Leadership

| Property | Required | Type | Description |
|---|---|---|---|
| `leadershipType` | yes | enum: `NONE`, `FUNCTIONAL`, `DISCIPLINARY` |  |
| `directReports` |  | [NumberRange](#common-numberrange) |  |

<a id="common-jobarchetype"></a>
### JobArchetype

A recurring kind of job. archetypeId is a stable identifier; occupationCodes link it to official classifications.

| Property | Required | Type | Description |
|---|---|---|---|
| `archetypeId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `occupationCodes` |  | array of [ClassificationCode](#common-classificationcode) |  |

<a id="common-organizationtype"></a>
### OrganizationType

Type: enum: `EMPLOYER`, `STAFFING_AGENCY`, `RECRUITMENT_CONSULTANCY`, `PUBLIC_EMPLOYMENT_SERVICE`, `OTHER`

<a id="common-sizeclass"></a>
### SizeClass

Headcount classes.

Type: enum: `EMPLOYEES_1_9`, `EMPLOYEES_10_49`, `EMPLOYEES_50_249`, `EMPLOYEES_250_999`, `EMPLOYEES_1000_PLUS`

<a id="common-organization"></a>
### Organization

| Property | Required | Type | Description |
|---|---|---|---|
| `name` |  | string (minLength 1) |  |
| `organizationType` |  | [OrganizationType](#common-organizationtype) |  |
| `industries` |  | array of [ClassificationCode](#common-classificationcode) |  |
| `sizeClass` |  | [SizeClass](#common-sizeclass) |  |
| `url` |  | [Uri](#common-uri) |  |

<a id="common-task"></a>
### Task

| Property | Required | Type | Description |
|---|---|---|---|
| `taskId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `category` |  | [ClassificationCode](#common-classificationcode) |  |
| `shareOfTimePercent` |  | number (minimum 0; maximum 100) |  |

<a id="common-proficiency"></a>
### Proficiency

Ordered: BASIC < INTERMEDIATE < ADVANCED < EXPERT.

Type: enum: `BASIC`, `INTERMEDIATE`, `ADVANCED`, `EXPERT`

<a id="common-cefrlevel"></a>
### CefrLevel

Ordered CEFR levels; NATIVE ranks above C2.

Type: enum: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `NATIVE`

<a id="common-competency"></a>
### Competency

| Property | Required | Type | Description |
|---|---|---|---|
| `competencyId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `code` |  | [ClassificationCode](#common-classificationcode) |  |
| `proficiency` |  | [Proficiency](#common-proficiency) |  |
| `yearsOfPractice` |  | number (minimum 0) |  |
| `lastUsedYear` |  | integer (minimum 1900; maximum 2100) |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-languageskill"></a>
### LanguageSkill

| Property | Required | Type | Description |
|---|---|---|---|
| `languageCode` | yes | [LanguageCode](#common-languagecode) |  |
| `cefrLevel` | yes | [CefrLevel](#common-cefrlevel) |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-qualificationtype"></a>
### QualificationType

Type: enum: `DEGREE`, `VOCATIONAL_QUALIFICATION`, `CERTIFICATION`, `LICENSE`, `OTHER`

<a id="common-qualification"></a>
### Qualification

| Property | Required | Type | Description |
|---|---|---|---|
| `qualificationId` | yes | [Identifier](#common-identifier) |  |
| `qualificationType` | yes | [QualificationType](#common-qualificationtype) |  |
| `label` | yes | [Text](#common-text) |  |
| `eqfLevel` |  | integer (minimum 1; maximum 8) |  |
| `fieldOfStudy` |  | [Text](#common-text) |  |
| `issuerName` |  | string |  |
| `completedOn` |  | [YearMonth](#common-yearmonth) |  |
| `validUntil` |  | [Date](#common-date) |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-domainexperience"></a>
### DomainExperience

Months of experience in a domain (function, industry or occupation).

| Property | Required | Type | Description |
|---|---|---|---|
| `domainId` | yes | [Identifier](#common-identifier) |  |
| `label` | yes | [Text](#common-text) |  |
| `code` |  | [ClassificationCode](#common-classificationcode) |  |
| `months` | yes | integer (minimum 0) |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-developmentpath"></a>
### DevelopmentPath

Type: enum: `LEADERSHIP`, `EXPERT`, `PROJECT`, `INTERNATIONAL`, `CROSS_FUNCTIONAL`, `FURTHER_EDUCATION`

<a id="common-development"></a>
### Development

| Property | Required | Type | Description |
|---|---|---|---|
| `paths` |  | array of [DevelopmentPath](#common-developmentpath) |  |
| `trainingDaysPerYear` |  | [NumberRange](#common-numberrange) |  |
| `description` |  | [Text](#common-text) |  |

<a id="common-starttiming"></a>
### StartTiming

Start window. For a candidate: earliest possible start and notice period. For a job: desired start window.

| Property | Required | Type | Description |
|---|---|---|---|
| `immediate` |  | boolean |  |
| `earliestStartDate` |  | [Date](#common-date) |  |
| `latestStartDate` |  | [Date](#common-date) |  |
| `noticePeriod` |  | object |  |

<a id="common-workauthorization"></a>
### WorkAuthorization

| Property | Required | Type | Description |
|---|---|---|---|
| `countryCode` | yes | [CountryCode](#common-countrycode) |  |
| `status` | yes | enum: `AUTHORIZED`, `REQUIRES_SPONSORSHIP` |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-domaincriterionid"></a>
### DomainCriterionId

Stable identifier in reverse-DNS form owned by whoever defines the criterion, e.g. org.example.healthcare.night_shift_willingness.

Type: string (pattern `^[a-z0-9]+(\.[a-z0-9-]+)+\.[a-z][a-z0-9_]*$`)

<a id="common-domaincriterion"></a>
### DomainCriterion

Optional domain-specific criterion. dataType fixes the type of value; unitCode (UN/CEFACT) is used for quantities. comparator is only meaningful on requirement and condition sides.

| Property | Required | Type | Description |
|---|---|---|---|
| `criterionId` | yes | [DomainCriterionId](#common-domaincriterionid) |  |
| `label` | yes | [Text](#common-text) |  |
| `definitionUrl` |  | [Uri](#common-uri) |  |
| `dataType` | yes | enum: `BOOLEAN`, `INTEGER`, `NUMBER`, `TEXT`, `CODE`, `CODE_LIST` |  |
| `unitCode` |  | string (pattern `^[A-Z0-9]{2,3}$`) |  |
| `value` | yes | any |  |
| `comparator` |  | enum: `EQUALS`, `AT_LEAST`, `AT_MOST`, `ANY_OF`, `ALL_OF` |  |
| `provenance` |  | [Provenance](#common-provenance) |  |

<a id="common-sourcerecord"></a>
### SourceRecord

Where an imported profile comes from: source reference, retrieval date, digest of the original data, source format, input kind, extraction quality and source content that could not be mapped. Keeps the reference to the original material without copying it. Values of unmapped content are never stored.

| Property | Required | Type | Description |
|---|---|---|---|
| `sourceUrl` | yes | [Uri](#common-uri) | URL of the source, or urn:sha256:<digest> when the data was provided as a file without URL. |
| `sourceFileName` |  | string (minLength 1) |  |
| `sourceRecordId` |  | string (minLength 1) | Identifier of the record in the source system (e.g. a reference number). |
| `retrievedAt` | yes | [DateTime](#common-datetime) |  |
| `sourceKind` | yes | enum: `JOB_AD_WEB_PAGE`, `JOB_BOARD_LISTING`, `EMAIL_ALERT`, `ATS_API`, `PLATFORM_EXPORT`, `PORTAL_PROFILE`, `DOCUMENT`, `MANUAL_ENTRY`, `OTHER` |  |
| `sourceFormat` |  | string (pattern `^[a-z0-9][a-z0-9.-]*$`) | Adapter format identifier, e.g. ba-bewerberprofil-text, linkedin-data-export-csv, json-resume-1, job-ad-text-de. |
| `inputKind` |  | enum: `STRUCTURED`, `TEXT` | STRUCTURED: fields mapped directly. TEXT: values extracted from free text or a PDF text layer; see extractionQuality. |
| `textDigest` |  | object | SHA-256 of the original text (UTF-8) the profile was derived from. |
| `importedBy` |  | object |  |
| `extractionQuality` |  | object | Result of the adapter's input checks. PASSED: all content recognized. REVIEW: profile produced, but some content was not interpreted or a check needs a human. REJECTED inputs produce no profile. |
| `unmapped` |  | array of object | Source fields or content not carried into the profile, with the reason. Only field names are recorded, never their values. |

<a id="common-fieldstatement"></a>
### FieldStatement

How one field of an imported profile relates to the source. EXPLICIT: stated verbatim. NORMALIZED: stated, converted into AJMS units, codes or enumerations. DERIVED: not stated, inferred by a named method. lossy marks a loss of meaning. A field without a statement in an imported profile is not covered by the source record; an absent field is UNKNOWN.

| Property | Required | Type | Description |
|---|---|---|---|
| `path` | yes | string (pattern `^(/[A-Za-z0-9@_.-]+)+$`) | JSON Pointer (RFC 6901) to the field in this document. |
| `statementKind` | yes | enum: `EXPLICIT`, `NORMALIZED`, `DERIVED` |  |
| `sourceExcerpt` |  | string (minLength 1) |  |
| `method` |  | [Identifier](#common-identifier) |  |
| `note` |  | string |  |
| `lossy` |  | boolean | true when the conversion loses meaning (e.g. a coarser scale, a dropped detail); the note says what is lost. |

<a id="common-requirementlevel"></a>
### RequirementLevel

REQUIRED: hard requirement. PREFERRED: desirable, not decisive on its own.

Type: enum: `REQUIRED`, `PREFERRED`

## `profile-reference.schema.json`

<a id="profile-reference-root"></a>
### AJMS ProfileReference v0.1

Minimal exchange convention: tells a recipient which profile exists, in which version and where it can be retrieved. Carries no profile content. Access control is the responsibility of the hosting or transport solution. Community Draft - not an adopted standard.

| Property | Required | Type | Description |
|---|---|---|---|
| `@context` | yes | [JsonLdContext](#common-jsonldcontext) |  |
| `@type` | yes | const `ProfileReference` |  |
| `profileId` | yes | [ProfileId](#common-profileid) |  |
| `profileType` | yes | enum: `CandidateProfile`, `JobProfile` |  |
| `schemaVersion` | yes | [SchemaVersion](#common-schemaversion) |  |
| `updatedAt` | yes | [DateTime](#common-datetime) |  |
| `profileView` | yes | enum: `FULL_PRIVATE`, `SHARED_VIEW`, `PUBLIC_MINIMAL`, `PUBLIC` |  |
| `profileUrl` | yes | string (pattern `^https://[^\s]+$`) | Where the profile document can be retrieved (https). Retrieval may require authorization by the host. |
| `accessMethod` | yes | enum: `PUBLIC`, `ACCESS_CONTROLLED`, `ON_REQUEST` | PUBLIC: no authorization. ACCESS_CONTROLLED: the host authorizes each request. ON_REQUEST: ask via accessRequestUrl first. |
| `accessRequestUrl` |  | string (pattern `^https://[^\s]+$`) |  |
| `mediaType` |  | enum: `application/ld+json`, `application/json` |  |
| `contentDigest` |  | object | Optional integrity hint over the referenced document (SHA-256 of its canonical JSON serialization, see docs/privacy-and-exchange.md). Not a signature: it does not prove who created the document. |
| `expiresAt` |  | [DateTime](#common-datetime) |  |
| `intendedRecipient` |  | string | Free-text label of the recipient a SHARED_VIEW is meant for. Not an access control mechanism. |

## `match-policy.schema.json`

<a id="match-policy-root"></a>
### AJMS MatchPolicy v0.1

Evaluation weights for one matching perspective, kept separate from profile data. Weights only rank WISH / PREFERRED criteria; hard conditions are never weighted. Community Draft - not an adopted standard.

| Property | Required | Type | Description |
|---|---|---|---|
| `@type` | yes | const `MatchPolicy` |  |
| `policyId` | yes | [Identifier](#common-identifier) |  |
| `schemaVersion` | yes | [SchemaVersion](#common-schemaversion) |  |
| `perspective` | yes | enum: `HIRING_FIT`, `CAREER_FIT` |  |
| `calibrationStatus` | yes | enum: `UNCALIBRATED`, `CALIBRATED` | UNCALIBRATED: weights are illustrative and were not validated against outcomes or user judgements. |
| `weights` | yes | object |  |
| `note` |  | string |  |

<a id="match-policy-hiringfitgroup"></a>
### HiringFitGroup

Type: enum: `competencies`, `languages`, `qualifications`, `domainExperience`, `totalExperience`, `leadershipExperience`, `careerLevel`, `workAuthorization`, `startTiming`, `domainCriteria`

<a id="match-policy-careerfitgroup"></a>
### CareerFitGroup

Type: enum: `archetype`, `careerLevel`, `industry`, `organization`, `tasks`, `compensation`, `location`, `workModel`, `workingTime`, `contract`, `development`, `domainCriteria`

<a id="match-policy-criteriongroup"></a>
### CriterionGroup

Type: [HiringFitGroup](#match-policy-hiringfitgroup) or [CareerFitGroup](#match-policy-careerfitgroup)

## `match-result.schema.json`

<a id="match-result-root"></a>
### AJMS MatchResult v0.1

Output of a bidirectional comparison. Hiring-Fit (does the candidate meet the job's requirements?) and Career-Fit (does the job meet the candidate's conditions and wishes?) are reported separately and never merged into one number. Community Draft - not an adopted standard.

| Property | Required | Type | Description |
|---|---|---|---|
| `@type` | yes | const `MatchResult` |  |
| `schemaVersion` | yes | [SchemaVersion](#common-schemaversion) |  |
| `candidateProfileId` | yes | [ProfileId](#common-profileid) |  |
| `candidateUpdatedAt` |  | [DateTime](#common-datetime) |  |
| `jobProfileId` | yes | [ProfileId](#common-profileid) |  |
| `jobUpdatedAt` |  | [DateTime](#common-datetime) |  |
| `hiringFit` | yes | [PerspectiveResult](#match-result-perspectiveresult) |  |
| `careerFit` | yes | [PerspectiveResult](#match-result-perspectiveresult) |  |
| `generatedBy` | yes | object |  |
| `disclaimer` |  | string |  |

<a id="match-result-outcome"></a>
### Outcome

MET, PARTIALLY_MET, NOT_MET, UNKNOWN (information missing or not comparable), NOT_APPLICABLE (criterion does not apply).

Type: enum: `MET`, `PARTIALLY_MET`, `NOT_MET`, `UNKNOWN`, `NOT_APPLICABLE`

<a id="match-result-criterionresult"></a>
### CriterionResult

| Property | Required | Type | Description |
|---|---|---|---|
| `criterionKey` | yes | string (pattern `^[A-Za-z]+(/[A-Za-z0-9._:-]+)?$`) |  |
| `group` | yes | string |  |
| `strength` | yes | enum: `HARD`, `SOFT` |  |
| `outcome` | yes | [Outcome](#match-result-outcome) |  |
| `explanation` | yes | string |  |

<a id="match-result-perspectiveresult"></a>
### PerspectiveResult

| Property | Required | Type | Description |
|---|---|---|---|
| `perspective` | yes | enum: `HIRING_FIT`, `CAREER_FIT` |  |
| `policyId` | yes | [Identifier](#common-identifier) |  |
| `calibrationStatus` | yes | enum: `UNCALIBRATED`, `CALIBRATED` |  |
| `hardConditionStatus` | yes | enum: `NONE_DEFINED`, `ALL_MET`, `NOT_MET`, `UNRESOLVED` | NONE_DEFINED, ALL_MET, NOT_MET (at least one hard criterion NOT_MET), UNRESOLVED (none NOT_MET, at least one UNKNOWN or PARTIALLY_MET). |
| `indicativeScore` | yes | number or null (minimum 0; maximum 1) | Weighted share of soft criteria met, computed only over criteria with a known outcome. null when no soft criterion is known. |
| `knownWeightCoverage` | yes | number (minimum 0; maximum 1) | Share of the total soft-criterion weight whose outcome is known. Read together with indicativeScore. |
| `outcomeCounts` | yes | object |  |
| `criteria` | yes | array of [CriterionResult](#match-result-criterionresult) |  |
