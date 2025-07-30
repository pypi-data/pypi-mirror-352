# nlcmd/parser.py

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from rapidfuzz import fuzz
# Assuming utils.py and its LOGGER_NAME are correctly set up
# and utils.py is in the same package directory.
from . import utils

# Attempt to load spaCy if the 'nlp' extra is installed
try:
    import spacy
    # Load a small English model. Disable only 'parser' to keep 'tagger' for lemmatizer.
    _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser"])
except (ImportError, OSError):
    _spacy_nlp = None
    logging.getLogger(utils.LOGGER_NAME).info(
        "spaCy or en_core_web_sm not found. "
        "NLP features like lemmatization and NER-based argument extraction will be limited or unavailable."
    )


class CommandParser:
    def __init__(self, commands: List[Dict[str, Any]]):
        """
        commands: list of {intent, tags, command} dicts
        """
        self.commands = commands
        self.logger = utils.setup_logger(logger_name=utils.LOGGER_NAME)
        if _spacy_nlp:
            self.logger.info("spaCy loaded successfully. Lemmatization (with POS tagging) and NER available.")
        else:
            self.logger.warning(
                "spaCy not available. Proceeding with basic text normalization and heuristics."
            )

    def _normalize_and_lemmatize(self, text: str) -> Tuple[str, List[str]]:
        """
        Normalize text and also return lemmatized tokens if spaCy is available.
        """
        normalized_text = utils.normalize_text(text)
        if _spacy_nlp:
            doc = _spacy_nlp(normalized_text) # Process normalized text for lemmas
            lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            lemmatized_query_string = " ".join(lemmas)
            self.logger.debug(f"Original: '{text}', Normalized: '{normalized_text}', Lemmatized Query: '{lemmatized_query_string}'")
            return normalized_text, lemmas
        self.logger.debug(f"Original: '{text}', Normalized: '{normalized_text}', No spaCy Lemmatization.")
        return normalized_text, normalized_text.split()


    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        Return a dictionary containing the best-matching command details,
        the filled command, and parsing status.
        """
        normalized_user_input, query_lemmas_or_tokens = self._normalize_and_lemmatize(user_input)

        best_score = 0.0
        best_entry: Optional[Dict[str, Any]] = None
        MIN_ACCEPTABLE_SCORE = 1.8

        self.logger.debug(f"Parsing user input: '{user_input}'")
        self.logger.debug(f"Normalized input for matching: '{normalized_user_input}', Query tokens/lemmas: {query_lemmas_or_tokens}")

        for entry in self.commands:
            intent_tags = entry.get("tags", [])
            joined_tags_string = " ".join(intent_tags)

            tag_occurrence_score = sum(1 for tag_word in intent_tags if tag_word in query_lemmas_or_tokens)
            fuzzy_score_tags_vs_query = fuzz.token_set_ratio(joined_tags_string, " ".join(query_lemmas_or_tokens)) / 100.0
            intent_name_score = fuzz.partial_ratio(entry.get("intent", ""), " ".join(query_lemmas_or_tokens)) / 100.0 * 0.5
            total_score = tag_occurrence_score + fuzzy_score_tags_vs_query + intent_name_score

            self.logger.debug(
                f"Intent='{entry['intent']}', Tags='{joined_tags_string}' | "
                f"TagOccurrence={tag_occurrence_score:.2f}, FuzzyTagsVsQuery={fuzzy_score_tags_vs_query:.2f}, "
                f"IntentNameScore={intent_name_score:.2f} | Total={total_score:.2f}"
            )

            if total_score > best_score:
                best_score = total_score
                best_entry = entry

        if best_entry and best_score >= MIN_ACCEPTABLE_SCORE:
            self.logger.info(
                f"Best match: Intent='{best_entry['intent']}' with score={best_score:.2f}"
            )
            fill_result = self.fill_template_arguments(best_entry, user_input, normalized_user_input)
            return {
                "intent_entry": best_entry,
                "score": best_score,
                "status": "success" if not fill_result.get("missing_args") else "needs_arguments",
                "filled_command": fill_result["filled_command"],
                "extracted_args": fill_result["extracted_args"],
                "missing_args": fill_result["missing_args"],
            }
        else:
            self.logger.info(f"No suitable command found for input. Best score {best_score:.2f} (threshold {MIN_ACCEPTABLE_SCORE}).")
            return {
                "intent_entry": None,
                "score": best_score,
                "status": "failure",
                "error_message": "No matching command intent found or score too low.",
            }

    def fill_template_arguments(
        self, intent_entry: Dict[str, Any], raw_user_input: str, normalized_user_input: str
    ) -> Dict[str, Any]:
        template_command = intent_entry["command"]
        placeholders = re.findall(r"\{([^}]+)\}", template_command)
        
        if not placeholders:
            return {
                "filled_command": template_command,
                "extracted_args": {},
                "missing_args": [],
            }

        self.logger.debug(f"Attempting to fill template: '{template_command}' for intent '{intent_entry['intent']}' with placeholders: {placeholders}")

        extracted_values: Dict[str, str] = {}
        intent_tags_and_command_keywords = set(intent_entry.get("tags", []))
        normalized_template_command_words = utils.normalize_text(template_command).split()
        for word in normalized_template_command_words:
            if not re.fullmatch(r"\{[^}]+\}", word): 
                 intent_tags_and_command_keywords.add(word)
        
        self.logger.debug(f"Normalized user input for arg extraction: {normalized_user_input}")
        self.logger.debug(f"Intent tags and command keywords to ignore for arg extraction: {intent_tags_and_command_keywords}")

        quoted_string_matches = re.findall(r'"([^"]+)"|\'([^\']+)\'', raw_user_input)
        available_quoted_strings = [item for tpl in quoted_string_matches for item in tpl if item]
        
        for ph in list(placeholders):
            if ph in extracted_values: continue
            if ph in ("message", "pattern", "text", "query", "old", "new", "content") and available_quoted_strings:
                extracted_values[ph] = available_quoted_strings.pop(0)
                self.logger.debug(f"Extracted '{extracted_values[ph]}' for placeholder '{ph}' (from quotes).")

        if _spacy_nlp:
            doc = _spacy_nlp(raw_user_input)
            self.logger.debug(f"NER Entities found: {[(ent.text, ent.label_) for ent in doc.ents]}")
            for ent in doc.ents:
                entity_text = ent.text
                entity_label = ent.label_
                potential_ph = None
                if entity_label in ("PERSON", "ORG") and "user" in placeholders and "user" not in extracted_values:
                    potential_ph = "user"
                elif entity_label == "GPE" and "host" in placeholders and "host" not in extracted_values:
                    potential_ph = "host"
                elif entity_label == "DATE" and "date" in placeholders and "date" not in extracted_values:
                    potential_ph = "date"
                
                if potential_ph and potential_ph in placeholders and potential_ph not in extracted_values:
                    extracted_values[potential_ph] = entity_text
                    self.logger.debug(f"Extracted '{entity_text}' for placeholder '{potential_ph}' (from NER {entity_label}).")

        temp_normalized_input_for_tokens = normalized_user_input
        for ph_val in extracted_values.values():
            normalized_ph_val = utils.normalize_text(ph_val)
            if normalized_ph_val:
                temp_normalized_input_for_tokens = temp_normalized_input_for_tokens.replace(normalized_ph_val, "", 1)
        
        all_tokens_for_args = [tok for tok in temp_normalized_input_for_tokens.split() if tok]

        candidate_arg_tokens = [
            tok for tok in all_tokens_for_args
            if tok not in intent_tags_and_command_keywords and \
               not tok.isnumeric() and \
               len(tok) > 1  # <--- ***** APPLIED FIX HERE ***** Filter out single-character non-numeric tokens
        ]
        candidate_numeric_tokens = [tok for tok in all_tokens_for_args if tok.isnumeric()]

        self.logger.debug(f"Candidate arg tokens (non-numeric, after filter & removing extracted): {candidate_arg_tokens}")
        self.logger.debug(f"Candidate numeric tokens: {candidate_numeric_tokens}")

        if "source" in placeholders and "destination" in placeholders and \
           "source" not in extracted_values and "destination" not in extracted_values:
            if len(candidate_arg_tokens) >= 2:
                extracted_values["source"] = candidate_arg_tokens.pop(0)
                extracted_values["destination"] = candidate_arg_tokens.pop(0)
                self.logger.debug(f"Extracted source='{extracted_values['source']}', destination='{extracted_values['destination']}' (heuristic).")
        
        for ph in placeholders:
            if ph in extracted_values:
                continue

            value_found = False
            if ph in ("pid", "count", "number") and candidate_numeric_tokens:
                extracted_values[ph] = candidate_numeric_tokens.pop(0)
                value_found = True
            elif candidate_arg_tokens:
                extracted_values[ph] = candidate_arg_tokens.pop(0)
                value_found = True
            
            if value_found:
                 self.logger.debug(f"Extracted '{extracted_values[ph]}' for placeholder '{ph}' (heuristic token).")

        missing_args = [ph for ph in placeholders if ph not in extracted_values]
        final_values_for_format = {ph: extracted_values.get(ph, f"{{{ph}}}") for ph in placeholders}

        try:
            filled_command = template_command.format(**final_values_for_format)
        except KeyError as e:
            self.logger.error(f"KeyError during command formatting: {e}. Placeholder might be malformed in template.")
            filled_command = template_command
        
        if missing_args:
            self.logger.warning(f"Missing arguments for intent '{intent_entry['intent']}': {missing_args}. Command after fill: '{filled_command}'")
        else:
            self.logger.info(f"All arguments filled for intent '{intent_entry['intent']}'. Command: '{filled_command}'")

        return {
            "filled_command": filled_command,
            "extracted_args": extracted_values,
            "missing_args": missing_args,
        }