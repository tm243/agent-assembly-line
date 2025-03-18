"""
Agent-Assembly-Line
"""

from src.middleware.semantic_test_case import SemanticTestCase
import unittest

longer_text = \
"""Saint Patrick's Day was made an official Christian feast day in the early 17th century and is observed by the Catholic Church, the Anglican Communion (especially the Church of Ireland),[7] the Eastern Orthodox Church, and the Lutheran Church. The day commemorates Saint Patrick and the arrival of Christianity in Ireland, and, by extension, celebrates the heritage and culture of the Irish in general.[5][8] Celebrations generally involve public parades and festivals, céilithe, and the wearing of green attire or shamrocks.[9] Christians who belong to liturgical denominations also attend church services.[8][10] Historically, the Lenten restrictions on fasting and drinking alcohol were lifted for the day, which has encouraged the holiday's tradition of revelry.[8][9][11][12]
Saint Patrick's Day is a public holiday in the Republic of Ireland,[13] Northern Ireland,[14] the Canadian province of Newfoundland and Labrador (for provincial government employees), and the British Overseas Territory of Montserrat. It is also widely celebrated in places with a large Irish diaspora community, such as Great Britain,[15] Canada, the United States, Australia, New Zealand, and South Africa.[16] Saint Patrick's Day is celebrated in more countries than any other national festival.[17] Modern celebrations have been greatly influenced by those of the Irish diaspora, particularly those that developed in North America. However, there has been criticism of Saint Patrick's Day celebrations for having become too commercialised and for fostering negative stereotypes of the Irish people.[18]
"""

class TestTextValidator(SemanticTestCase):
    """
    We're testing the SemanticTestCase here
    """

    def test_semantic(self):
        self.assertSemanticallyCorrect(longer_text, "It is a public holiday in Ireland")
        self.assertSemanticallyIncorrect(longer_text, "It is a public holiday in Italy")
        self.assertSemanticallyEqual("Blue is the sky.", "The sky is blue.")

if __name__ == "__main__":
    unittest.main()
