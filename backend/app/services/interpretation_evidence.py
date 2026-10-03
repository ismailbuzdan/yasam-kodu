"""Deterministic Phase 1 semantic evidence matching; no provider or prose generation."""
from app.schemas.interpretation import InterpretationInput
from app.services.interpretation_ai_models import (
    EVIDENCE_VERSION, FactPredicate, InterpretationFoundationError, SemanticEvidenceUnit,
)

_PROTOTYPE_SOURCE = ("project-authored-prototype",)
_PROTOTYPE_STATUS = "foundation_prototype_not_production_qualified"
_PROTOTYPE_LICENSE = "project_authored_prototype"


ASTROLOGY_FOUNDATION_CATALOG = (
    SemanticEvidenceUnit(
        unit_id="astro.sun.aries.house1.initiative.v1", version=EVIDENCE_VERSION,
        status=_PROTOTYPE_STATUS, system="astrology",
        required_facts=(FactPredicate(path="astrology.bodies.sun.sign", expected="aries"),
                        FactPredicate(path="astrology.bodies.sun.house", expected=1)),
        public_basis=("astrology.bodies.sun.sign", "astrology.bodies.sun.house"),
        allowed_sections=("basic_triad", "strengths"),
        allowed_statement_tr=("Astrolojik yorumda bu yerleşim girişim ve bireysel inisiyatif "
                              "temalarıyla ilişkilendirilebilir."),
        allowed_themes=("initiative", "self_expression"),
        forbidden_extensions=("impatience", "regret", "certain_behavior"),
        source_ids=_PROTOTYPE_SOURCE, license_classification=_PROTOTYPE_LICENSE,
    ),
    SemanticEvidenceUnit(
        unit_id="astro.moon.libra.house7.relational_balance.v1", version=EVIDENCE_VERSION,
        status=_PROTOTYPE_STATUS, system="astrology",
        required_facts=(FactPredicate(path="astrology.bodies.moon.sign", expected="libra"),
                        FactPredicate(path="astrology.bodies.moon.house", expected=7)),
        public_basis=("astrology.bodies.moon.sign", "astrology.bodies.moon.house"),
        allowed_sections=("basic_triad", "strengths"),
        allowed_statement_tr=("Astrolojik yorumda bu yerleşim ilişkisel denge ve uyum temalarıyla "
                              "ilişkilendirilebilir."),
        allowed_themes=("relational_balance", "harmony"),
        forbidden_extensions=("regret", "diagnosis", "certain_behavior"),
        source_ids=_PROTOTYPE_SOURCE, license_classification=_PROTOTYPE_LICENSE,
    ),
    SemanticEvidenceUnit(
        unit_id="astro.ascendant.aries.direct_expression.v1", version=EVIDENCE_VERSION,
        status=_PROTOTYPE_STATUS, system="astrology",
        required_facts=(FactPredicate(path="astrology.ascendant", expected="aries"),),
        public_basis=("astrology.ascendant",), allowed_sections=("basic_triad", "strengths"),
        allowed_statement_tr=("Astrolojik yorumda Koç yükselen doğrudan kendini ifade etme temasıyla "
                              "ilişkilendirilebilir."),
        allowed_themes=("direct_expression",),
        forbidden_extensions=("impulsiveness", "impatience", "regret", "certain_behavior"),
        source_ids=_PROTOTYPE_SOURCE, license_classification=_PROTOTYPE_LICENSE,
    ),
    SemanticEvidenceUnit(
        unit_id="astro.mc.capricorn.long_term_structure.v1", version=EVIDENCE_VERSION,
        status=_PROTOTYPE_STATUS, system="astrology",
        required_facts=(FactPredicate(path="astrology.mc", expected="capricorn"),),
        public_basis=("astrology.mc",), allowed_sections=("basic_triad", "strengths"),
        allowed_statement_tr=("Astrolojik yorumda Oğlak MC uzun vadeli yapı ve sorumluluk "
                              "temalarıyla ilişkilendirilebilir."),
        allowed_themes=("long_term_structure", "responsibility"),
        forbidden_extensions=("career_success", "certain_outcome"),
        source_ids=_PROTOTYPE_SOURCE, license_classification=_PROTOTYPE_LICENSE,
    ),
    SemanticEvidenceUnit(
        unit_id="astro.sun_moon.opposition.theme_tension.v1", version=EVIDENCE_VERSION,
        status=_PROTOTYPE_STATUS, system="astrology",
        required_facts=(FactPredicate(path="astrology.aspects.0.body1", expected="sun"),
                        FactPredicate(path="astrology.aspects.0.body2", expected="moon"),
                        FactPredicate(path="astrology.aspects.0.type", expected="opposition"),
                        FactPredicate(path="astrology.bodies.sun.sign", expected="aries"),
                        FactPredicate(path="astrology.bodies.moon.sign", expected="libra")),
        public_basis=("astrology.aspects.0.type", "astrology.bodies.sun.sign",
                      "astrology.bodies.moon.sign"),
        allowed_sections=("challenges",),
        allowed_statement_tr=("Astrolojik yorumda Güneş-Ay karşıtlığı, temsil edilen temalar arasında "
                              "denge arayışı olarak yorumlanabilir."),
        allowed_themes=("theme_tension", "balance"),
        forbidden_extensions=("regret", "diagnosis", "certain_behavior"),
        source_ids=_PROTOTYPE_SOURCE, license_classification=_PROTOTYPE_LICENSE,
    ),
)


def _fact_values(input: InterpretationInput) -> dict[str, object]:
    values: dict[str, object] = {}
    astrology = input.astrology
    if astrology is None:
        return values
    for body in astrology.bodies:
        prefix = f"astrology.bodies.{body.body}"
        values[f"{prefix}.sign"] = body.sign
        values[f"{prefix}.retrograde"] = body.retrograde
        if body.house is not None:
            values[f"{prefix}.house"] = body.house
    if astrology.ascendant is not None:
        values["astrology.ascendant"] = astrology.ascendant
    if astrology.mc is not None:
        values["astrology.mc"] = astrology.mc
    for house in astrology.houses:
        values[f"astrology.houses.{house.house}.sign"] = house.sign
    for index, aspect in enumerate(astrology.aspects):
        prefix = f"astrology.aspects.{index}"
        values[f"{prefix}.body1"] = aspect.body1
        values[f"{prefix}.body2"] = aspect.body2
        values[f"{prefix}.type"] = aspect.type
    return values


class SemanticEvidenceBuilder:
    """Match exact predicates and return a canonical unit-id ordering."""

    def __init__(self, catalog: tuple[SemanticEvidenceUnit, ...] = ASTROLOGY_FOUNDATION_CATALOG):
        ids = tuple(unit.unit_id for unit in catalog)
        if len(ids) != len(set(ids)):
            raise InterpretationFoundationError("invalid_catalog")
        self._catalog = tuple(sorted(catalog, key=lambda unit: unit.unit_id))

    def build(self, input: InterpretationInput) -> tuple[SemanticEvidenceUnit, ...]:
        if type(input) is not InterpretationInput:
            raise InterpretationFoundationError("invalid_catalog")
        facts = _fact_values(input)
        # Missing/unknown paths do not match. They never become permissive wildcards.
        return tuple(unit for unit in self._catalog if all(
            predicate.path in facts and facts[predicate.path] == predicate.expected
            for predicate in unit.required_facts
        ))
