from unittest import TestCase
from uw_adsel import AdSelAzure
from uw_adsel.models import CohortAssignment


class AdselTest(TestCase):
    adsel = AdSelAzure()
    cohort = CohortAssignment(cohort_number=1, campus=2)

    def test_bulk_assign(self):
        submit = self.adsel.assign_cohorts_bulk(self.cohort)
        self.assertEqual(submit["response"], {'string_response': ''})

    def test_pugo_assign(self):
        submit = self.adsel.assign_pugo(self.cohort)
        self.assertEqual(submit["response"], {'string_response': 'asd'})
