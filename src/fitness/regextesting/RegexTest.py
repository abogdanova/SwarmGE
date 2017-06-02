

class RegexTest:
    """
    Class which contains a test string and matches
    (We should probably just use the types which re library uses)
    """
        
    def __init__(self, search_string):
        
        # print("Added regex search string: "+search_string)
        self.search_string = search_string
        self.matches = []

    def add_match(self, start, end):
        
        self.matches.append({'start': start,
                             'end': end,
                             'matched_string': self.search_string[start:end]})
        
    def calc_match_errors(self, match_candidates):

        undesired_range = missing_range = 0

        for a_known_match in self.matches:
            # missing any of the desired extraction costs a lot
            missing_range += self.find_missing_range(a_known_match,
                                                     match_candidates)
        for match_candidate in match_candidates:
            undesired_range += self.find_undesired_range(match_candidate,
                                                         self.matches)

        match_error = missing_range + undesired_range
        match_error += (abs(len(match_candidates) - len(self.matches)))

        return match_error

    def get_search_string(self):
        
        return self.search_string

    def find_missing_range( a_known_match, match_ranges):
        start = a_known_match.get("start")
        end = a_known_match.get("end")
        missing = end - start
        
        for i in range(start, end):
            found = False
            
            for m_range in match_ranges:
                
                if m_range.start() <= i < m_range.end():
                    found = True
            
            if found:
                missing -= 1
        
        return missing

    def find_undesired_range( match_candidate, known_matches):
        undesired_matched = 0
        
        for i in range(match_candidate.start(), match_candidate.end()):
            in_range = False
        
            for a_known_match in known_matches:
                start = a_known_match.get("start")
                end = a_known_match.get("end")
        
                if start <= i <= end:
                    in_range = True
            
            if not in_range:
                undesired_matched += 1
        
        return undesired_matched
