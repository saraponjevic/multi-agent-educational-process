// Fiksne oznake: boje faza, lepa imena artefakata i nivoa ucenika.

export const PHASE_COLORS = ['var(--p1)', 'var(--p2)', 'var(--p3)', 'var(--p4)']

export const ARTIFACT_TITLES = {
  learning_outcomes: 'Nastavni ishodi',
  curriculum_structure: 'Nastavni plan',
  competency_identification: 'Kompetencije',
  achievement_indicators: 'Pokazatelji ostvarenosti',
  curriculum_documentation: 'Dokumentacija kurikuluma',
  lesson_generator: 'Lekcije',
  example_generator: 'Zbirka rešenih primera',
  exercise_generator: 'Zadaci',
  exercise_solver: 'Provera zadataka (rešavač)',
  material_quality_check: 'Provera kvaliteta materijala',
  formatting_export: 'Materijali (kurikulum, lekcije, zadaci)',
  teacher: 'Delovi lekcije (čas)',
  knowledge_state: 'Stanje znanja učenika',
  test_generator: 'Test',
  test_taking: 'Odgovori učenika na testu',
  answer_grader: 'Ocene',
  quality_evaluator: 'Ocena kvaliteta',
  optimizer: 'Predlozi za doradu',
  feedback_manager: 'Odluka o doradi',
  final_report: 'Završni izveštaj',
  materijali: 'Svi materijali (markdown)',
}

const LEVEL_NAMES = { beginner: 'početnik', intermediate: 'srednji', advanced: 'napredni' }

export function studentLabel(system, id) {
  const s = (system?.students || []).find((x) => x.id === id)
  const level = s?.params?.level || id
  return LEVEL_NAMES[level] || level
}

export function phaseShortName(name) {
  return String(name || '').replace(/^Faza \d+ - /, '')
}
