import os
import sys

from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Table, Domain, ContinuousVariable
from thefuzz import fuzz
from AnyQt.QtWidgets import QApplication

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWKeywords(widget.OWWidget):
    name = "Keywords Detection"
    description = "Give the amount of keywords from in_object in in_data"
    icon = "icons/keyword.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/keyword.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owkeyword.ui")
    want_control_area = False
    priority = 1050

    class Inputs:
        data = Input("Content", Table)
        keywords = Input("Keywords", Table)

    class Outputs:
        data = Output("Keywords per Content", Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.keywords = None
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        self.autorun = True

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.autorun and self.keywords:
            self.process()

    @Inputs.keywords
    def set_keywords(self, in_keywords):
        self.keywords = in_keywords
        if self.autorun and self.data:
            self.process()

    def fuzzy_match_score_with_keywords(self, text, keywords, threshold=80):
        """
        Returns fuzzy global score and matched keywords.
        """
        words = text.split(" ")
        total_score = 0
        matched_keywords = []

        for keyword in keywords:
            best_score = max(fuzz.ratio(word.lower(), keyword.lower()) for word in words)
            if best_score >= threshold:
                matched_keywords.append(keyword)
                total_score += best_score

        if not matched_keywords:
            return 0.0, []

        avg_score = total_score / len(keywords)
        return avg_score, matched_keywords

    def extract_matched_keywords(self, text, keywords, threshold=80):
        """
        Extracts matched keywords from a text using fuzzy matching.

        Args:
            text (str): The input string to analyze.
            keywords (list): A list of keywords to match against.
            threshold (int): Minimum fuzzy ratio to consider a match.

        Returns:
            list: Keywords that match the text above the threshold.
        """
        words = text.split(" ")
        matched_keywords = []

        for keyword in keywords:
            best_score = max(fuzz.ratio(word.lower(), keyword.lower()) for word in words)
            if best_score >= threshold:
                matched_keywords.append(keyword)

        return matched_keywords

    def process(self):
        if self.data is None or self.keywords is None:
            print("[INFO] No input data or keywords provided.")
            return

        if "Content" not in self.data.domain:
            self.error("Missing 'Content' column in input data")
            print("[ERROR] 'Content' column not found in input data.")
            return

        self.error("")  # Clear previous errors

        # Extraction des mots-clés
        try:
            if "Keywords" not in self.keywords.domain:
                self.error("Missing 'Keywords' column in keywords table")
                print("[ERROR] 'Keywords' column not found in keyword input.")
                return

            keyword_list = [str(row["Keywords"]) for row in self.keywords if str(row["Keywords"]).strip() != ""]
            print(f"[INFO] Extracted {len(keyword_list)} keywords: {keyword_list}")
        except Exception as e:
            self.error("Error while extracting keywords")
            print(f"[EXCEPTION] Failed to extract keywords: {e}")
            return

        # Création du nouveau domaine avec uniquement la colonne "Keywords"
        new_metas_vars = list(self.data.domain.metas)

        if not any(var.name == "Keywords" for var in new_metas_vars):
            new_metas_vars.append(ContinuousVariable("Keywords"))

        new_domain = Domain(
            self.data.domain.attributes,
            self.data.domain.class_vars,
            new_metas_vars
        )

        # Fonction de score
        def fuzzy_match_score(text, keywords, threshold=80):
            words = text.split(" ")
            total_score = 0
            matched = 0

            for keyword in keywords:
                best_score = max(fuzz.ratio(word.lower(), keyword.lower()) for word in words)
                if best_score >= threshold:
                    total_score += best_score
                    matched += 1

            if matched == 0:
                return 0.0
            return total_score / len(keywords)

        # Construction des nouvelles métadonnées
        new_metas = []
        for i, row in enumerate(self.data):
            text = str(row["Content"])
            score = fuzzy_match_score(text, keyword_list)
            print(f"[DEBUG] Row {i}: Score = {score:.2f}")
            new_metas.append(list(row.metas) + [score])

        out_data = Table(new_domain, self.data.X, self.data.Y, new_metas)
        print("[INFO] Process complete. Sending output data.")
        self.Outputs.data.send(out_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ow = OWKeywords()
    ow.show()
    app.exec_()
