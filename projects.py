#!/usr/bin/env python3

import configparser

class AnnifProject:
    def __init__(self, project_id, config):
        self.project_id = project_id
        self.config = config
    
    def get_index_name(self):
        return self.config['indexname']
    
    def get_language(self):
        return self.config['language']
    
    def get_analyzer(self):
        return self.config['analyzer']
    
    def get_corpus_pattern(self):
        return self.config['corpuspattern']
    

class AnnifProjects:
    """represents the available projects, emulating a read-only dict-like mapping of project id's to AnnifProject objects"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(['conf/projects.ini', '/etc/annif/projects.ini'])

    def __getitem__(self, project_id):
        """return an AnnifProject with the given id"""
        return AnnifProject(project_id, self.config[project_id])

    def __iter__(self):
        """iterate over the available project IDs"""
        return iter(self.config.sections())
    
    def __contains__(self, project_id):
        return (project_id in self.config)
    
    def __len__(self):
        return len(self.config.sections())


if __name__ == '__main__':
    # Test utility that just prints out the current project configuration
    projects = AnnifProjects()
    for project_id in projects:
        print("Project:", project_id)
        proj = projects[project_id]
        print("\tindex name:\t", proj.get_index_name())
        print("\tlanguage:\t", proj.get_language())
        print("\tanalyzer:\t", proj.get_analyzer())
        print("\tcorpus pattern:\t", proj.get_corpus_pattern())
