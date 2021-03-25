from django.test import TestCase
from app.scan import get_stats, poem_stats, original_scan, house_robber_scan, record, syllables
from app.models import Pronunciation


class TestStats(TestCase):
    @classmethod
    def setUpTestData(cls):
        Pronunciation.objects.create(word="the", stresses="u", popularity=381)
        Pronunciation.objects.create(word="the", stresses="/", popularity=4)
        Pronunciation.objects.create(word="moon", stresses="u", popularity=1)
        Pronunciation.objects.create(word="moon", stresses="/", popularity=15)
        Pronunciation.objects.create(word="is", stresses="u", popularity=89)
        Pronunciation.objects.create(word="is", stresses="/", popularity=29)
        Pronunciation.objects.create(word="a", stresses="u", popularity=149)
        Pronunciation.objects.create(word="a", stresses="/", popularity=1)
        Pronunciation.objects.create(word="wavering", stresses="/uu", popularity=1)
        Pronunciation.objects.create(word="rim", stresses="u", popularity=2)
        Pronunciation.objects.create(word="rim", stresses="/", popularity=1)
        Pronunciation.objects.create(word="where", stresses="u", popularity=11)
        Pronunciation.objects.create(word="where", stresses="/", popularity=14)
        Pronunciation.objects.create(word="one", stresses="u", popularity=15)
        Pronunciation.objects.create(word="one", stresses="/", popularity=4)
        Pronunciation.objects.create(word="fish", stresses="u", popularity=2)
        Pronunciation.objects.create(word="fish", stresses="/", popularity=1)
        Pronunciation.objects.create(word="slips", stresses="/", popularity=1)
        Pronunciation.objects.create(word="water", stresses="/u", popularity=3)
        Pronunciation.objects.create(word="makes", stresses="u", popularity=1)
        Pronunciation.objects.create(word="makes", stresses="/", popularity=4)
        Pronunciation.objects.create(word="quietness", stresses="/uu", popularity=1)
        Pronunciation.objects.create(word="quietness", stresses="/u/", popularity=1)
        Pronunciation.objects.create(word="of", stresses="u", popularity=152)
        Pronunciation.objects.create(word="of", stresses="/", popularity=60)
        Pronunciation.objects.create(word="sound", stresses="u", popularity=1)
        Pronunciation.objects.create(word="sound", stresses="/", popularity=3)
        Pronunciation.objects.create(word="night", stresses="u", popularity=2)
        Pronunciation.objects.create(word="night", stresses="/", popularity=12)
        Pronunciation.objects.create(word="an", stresses="u", popularity=11)
        Pronunciation.objects.create(word="anchoring", stresses="/u/", popularity=1)
        Pronunciation.objects.create(word="many", stresses="/u", popularity=4)
        Pronunciation.objects.create(word="ships", stresses="/", popularity=2)
        Pronunciation.objects.create(word="homebound", stresses="u/", popularity=1)
        Pronunciation.objects.create(word="beloved", stresses="u/", popularity=1)
        Pronunciation.objects.create(word="beloved", stresses="u/u", popularity=1)




    def test_capitalization(self):
        print(get_stats("the"))
        self.assertEqual(get_stats("the"), get_stats("THE"))

    def test_punctuation1(self):
        self.assertEqual(get_stats("sound;"), get_stats("sound"))

    def test_punctuation_capitalization(self):
        self.assertEqual(get_stats("Home-bound"), get_stats("homebound"))

    def test_unknown(self):
        self.assertEqual(get_stats("squirrel"), ["?", "?"])

    def test_one_instance(self):
        self.assertEqual(get_stats("an"), [0.0091])

    def test_multiple_instances(self):
        self.assertEqual(get_stats("beloved"), [0.0000, 100.0000, 0.0000])

    def test_diff_stress_patterns(self):
        self.assertEqual(get_stats("quietness"), [200.0000, 0.0000, 0.9901])

    def test_line_stats(self):
        line = "THE moon is a wavering rim where one fish slips,"
        scansion = [[0.0105, " ", 14.8515, " ", 0.3258,  " ", 0.0067, " ",
                     2.0000, 0.1000, 0.1000, " ", 0.4975, " ", 1.2716, " ",
                     0.2665, " ", 0.4975, " ", 2.0000, " "]]
        self.assertEqual(poem_stats(line), scansion)

    def test_poem_stats(self):
        poem = """THE moon is a wavering rim where one fish slips,
                The water makes a quietness of sound;
                Night is an anchoring of many ships
                Home-bound."""
        scansion = [[0.0105, " ", 14.8515, " ", 0.3258,  " ", 0.0067, " ",
                     2.0000, 0.1000, 0.1000, " ", 0.4975, " ", 1.2716, " ",
                     0.2665, " ", 0.4975, " ", 2.0000, " "],
                    [0.0105, " ", 6.000, 0.0333, " ", 3.9604, " ", 0.0067, " ",
                     200.0000, 0.0000, 0.9901, " ", 0.3947, " ", 2.9703, " "],
                    [5.9701, " ", 0.3258, " ", 0.0091, " ", 2.0, .1, 2.0, " ",
                     0.3947, " ", 8.0, 0.0250, " ", 4.0, " "],
                    [0.1, 2.0, " "]]
        self.assertEqual(poem_stats(poem), scansion)
    def test_line_with_unknown(self):
        line = "The moon is a wavering squirrel where one fish runs"
        scansion = [[0.0105, " ", 14.8515, " ", 0.3258,  " ", 0.0067, " ",
                     2.0000, 0.1000, 0.1000, " ", "?", "?", " ", 1.2716, " ",
                     0.2665, " ", 0.4975, " ", "?", " "]]
        self.assertEqual(poem_stats(line), scansion)

    def test_original_unambiguous(self):
        self.assertEqual(original_scan("water moon"), "/u / ")

    def test_original_punctuation_capitalization(self):
        self.assertEqual(original_scan("Wa'ter, moon."),
                         original_scan("water moon"))

    def test_original_equal(self):
        self.assertEqual(original_scan("is is"), "? ? ")

    def test_original_unknown(self):
        self.assertEqual(original_scan("squirrel"), "?? ")

    def test_original_unknown_comparison_unstressed(self):
        self.assertEqual(original_scan("the squirrel"), "u ?? ")

    def test_original_unknown_comparison_stressed(self):
        self.assertEqual(original_scan("moon squirrel"), "/ ?? ")

    def test_original_unknown_comparison_ambiguous(self):
        self.assertEqual(original_scan("is squirrel"), "? ?? ")

    def test_end_of_line(self):
        poem = "the moon is\nthe squirrel"
        self.assertEqual(original_scan(poem), "u / u \nu ?? ")

    def test_original_multiline(self):
        poem = "is squirrel\nmoon squirrel\nthe water moon"
        self.assertEqual(original_scan(poem), "? ?? \n/ ?? \nu /u / ")

    def test_house_robber_unambiguous(self):
        self.assertEqual(house_robber_scan("water moon"), "/u / ")

    def test_house_robber_punctuation_capitalization(self):
        self.assertEqual(house_robber_scan("Wa'ter, moon."),
                         house_robber_scan("water moon"))

    def test_house_robber_equal(self):
        self.assertEqual(house_robber_scan("is is"), "u / ")

    def test_house_robber_never_skip_three(self):
        line = "the moon of is the night"
        self.assertEqual(house_robber_scan(line), "u / u / u / ")

    def test_house_robber_find_obvious_anapest(self):
        self.assertEqual(house_robber_scan("water the moon"), "/u u / ")

    def test_house_robber_never_adjacent(self):
        self.assertEqual(house_robber_scan("moon water"), "/ u/ ")

    def test_house_robber_unknown(self):
        self.assertEqual(house_robber_scan("squirrel"), "u/ ")

    def test_house_robber_unstressed_unknown(self):
        self.assertEqual(house_robber_scan("the bird"), "u / ")

    def test_house_robber_stressed_unknown(self):
        self.assertEqual(house_robber_scan("moon bird"), "/ u ")

    def test_record_unknown(self):
        record("cat", "/")
        w = Pronunciation.objects.filter(word="cat")
        self.assertEqual(len(w), 1)
        self.assertEqual((w[0].stresses, w[0].popularity), ("/", 1))

    def test_record_known(self):
        record("moon", "/")
        w = Pronunciation.objects.filter(word="moon").order_by("-popularity")
        self.assertEqual(len(w), 2)
        self.assertEqual((w[0].stresses, w[0].popularity), ("/", 16))
        self.assertEqual((w[1].stresses, w[1].popularity), ("u", 1))

    def test_capitalization_punctuation(self):
        record("Mo'on", "/")
        w = Pronunciation.objects.filter(word="moon").order_by("-popularity")
        self.assertEqual(w[0].popularity, 16)

    def test_record_new_pron(self):
        record("wavering", "/u/")
        w = Pronunciation.objects.filter(word="wavering")
        self.assertEqual((w[0].stresses, w[0].popularity,
                          w[1].stresses, w[1].popularity),
                         ("/uu", 1, "/u/", 1))

    def test_simple_syll(self):
        self.assertEqual(syllables("squirrel"), 2)

    def test_vowel_split_diacritical(self):
        self.assertEqual(syllables("plié"), 2)
        self.assertEqual(syllables("neé"), 1)

    def test_vowel_split_ao(self):
        self.assertEqual(syllables("chaos"), 2)

    def test_vowel_split_eo(self):
        self.assertEqual(syllables("eon"), 2)
        self.assertEqual(syllables("righteous"), 2)

    def test_vowel_split_ia(self):
        self.assertEqual(syllables("diacritical"), 5)
        self.assertEqual(syllables("egalitarian"), 6)
        self.assertEqual(syllables("electrician"), 4)
        self.assertEqual(syllables("fustian"), 2)

    def test_vowel_split_ie(self):
        self.assertEqual(syllables("tries"), 1)
        self.assertEqual(syllables("quiet"), 2)

    def test_vowel_split_io(self):
        self.assertEqual(syllables("viol"), 2)
        self.assertEqual(syllables("perdition"), 3)
        self.assertEqual(syllables("suspicious"), 3)

    def test_vowel_split_iu(self):
        self.assertEqual(syllables("sodium"), 3)
        self.assertEqual(syllables("Lucius"), 2)

    def test_vowel_split_ua(self):
        self.assertEqual(syllables("duality"), 4)
        self.assertEqual(syllables("quality"), 3)
        self.assertEqual(syllables("Guam"), 1)

    def test_vowel_split_ue(self):
        self.assertEqual(syllables("quell"), 1)
        self.assertEqual(syllables("suet"), 2)
        self.assertEqual(syllables("cruel"), 2)
        self.assertEqual(syllables("due"), 1)

    def test_vowel_split_uo(self):
        self.assertEqual(syllables("duo"), 2)
        self.assertEqual(syllables("quote"), 1)

    def test_vowel_split_vowel_ing(self):
        self.assertEqual(syllables("crying"), 2)
        self.assertEqual(syllables("seeing"), 2)

    def test_vowel_split_consonant_y(self):
        self.assertEqual(syllables("mayor"), 2)

    def test_silent_final_e(self):
        self.assertEqual(syllables("sabre"), 2)
        self.assertEqual(syllables("battle"), 2)
        self.assertEqual(syllables("undue"), 2)
        self.assertEqual(syllables("vague"), 1)
        self.assertEqual(syllables("mare"), 1)

    def test_silent_final_ed_es(self):
        self.assertEqual(syllables("aided"), 2)
        self.assertEqual(syllables("parted"), 2)
        self.assertEqual(syllables("mitred"), 2)
        self.assertEqual(syllables("battled"), 2)
        self.assertEqual(syllables("aped"), 1)
        self.assertEqual(syllables("ached"), 1)
        self.assertEqual(syllables("tabbed"), 1)
        self.assertEqual(syllables("aides"), 1)
        self.assertEqual(syllables("mitres"), 2)
        self.assertEqual(syllables("ages"), 2)
        self.assertEqual(syllables("battles"), 2)
        self.assertEqual(syllables("hatches"), 2)
        self.assertEqual(syllables("lathes"), 1)
        self.assertEqual(syllables("paled"), 1)
        self.assertEqual(syllables("pared"), 1)
        self.assertEqual(syllables("pales"), 1)
        self.assertEqual(syllables("pares"), 1)
        self.assertEqual(syllables("barres"), 1)
        self.assertEqual(syllables("awes"), 1)
