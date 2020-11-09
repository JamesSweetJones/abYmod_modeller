#!/usr/bin/env python3
"""
Program: AbYMod_Modeller
File: abYmod_RPC.py
Version: 1.0
Date: 5/11/2020
Author: James Sweet-Jones
Address: Institute of Structural and Molecular Biology, Division of Biosciences, University College London
#############################################################################
Description:
===========

Takes in paired antibody light and heavy chain protein sequences and outputs model PDB files of models that were successfully built
#############################################################################

Usage:
=======

abYmod_RPC.py [x]

where x is a fasta-formatted file where identifiers and sequences are wrapped


>8E10_L|8E10 - (HUMAN) human
EIVLTQSPGTLSLSPGERATLSCRASQSVSSSYLAWYQQKPGQAPRLLIYGASSRATGIPDRFSGSGSGTDFTLTISRLEPADFAVYYCQQYGSSPSITFGQGTRLEIKR
>8E10_H|8E10 - (HUMAN) human
QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYAMHWVRQAPGQRLEWMGWINAGNGNTKYSQKFQGRVTITRDTSASTAYMELSSLRSEDTAVYYCARAMILRIGHGQPQGYWGEGTLVT


Light and heavy chains must be noted in the identifiers with "L|" or "H|" where light chains preceed their paired heavy chain
All sequences in input fasta file must be paired in this format otherwise this version of the script won't work!
**WARNING** if identifier has "/" character, this will be converted into "|" for purposes of writing output **WARNING**


#############################################################################
Revision History:
================

v1.0 - first commit

"""
#############################################################################
#Import libraries

import sys
import re
import os
from urllib import request
from time import sleep

#############################################################################


def model_structure(light_chain_identifier,light_chain,heavy_chain):
    """
    Input: wrapped fasta file
    Output: .pdb file of the paired antibody heavy and light chains
    """
    antibody_identifier_split = light_chain_identifier.split("|") #get antibody identifier
    antibody_identifier = antibody_identifier_split[1]

    antibody_identifier_name = antibody_identifier.replace("\/", "\|" )
    url          = "http://abymod.abysis.org/"\
                   "abymod_service.cgi"
    build_url    = url + "?" + "light=" + light_chain + "&heavy=" + heavy_chain
    print(build_url)
    UID          = request.urlopen(build_url).read() #Enter model to abYmod and get UID
    UID          = str(UID, encoding='utf-8')
    retrieve_url = url + "?" + "pdb=" + UID
    metadata_url = url + "?" + "json=" + UID
    log_url      = url + "?" + "log=" + UID
    output          = open("abYmod_modelling_" + antibody_identifier_name + ".pdb", 'w+') #Write pbd to file
    output_metadata = open("abYmod_metadata_" + antibody_identifier_name + ".txt", "w+") #write metadata to separate file
    retrieve_model  = request.urlopen(retrieve_url).read() #retreive pbd
    retrieve_model  = str(retrieve_model, encoding='utf-8')
    retrieve_log    = request.urlopen(log_url).read()
    retrieve_log    = str(retrieve_log, encoding='utf-8')
    print(retrieve_model)
     #Need to keep refreshing page until pbd file is written, need to find suitable loop for the job
    while retrieve_model == "0":
        if retrieve_log != "1":
            print("constructing model of ", light_chain_identifier, " ...")
            retrieve_model  = request.urlopen(retrieve_url).read() #retreive pbd
            retrieve_model  = str(retrieve_model, encoding='utf-8')
            sleep(10)
            if retrieve_model == "1":
                print("model of ", light_chain_identifier, " could not be constructed")
                break
            if retrieve_model != "0" and retrieve_model != "1":
                print("model complete")
                output            = open("abYmod_modelling_" + antibody_identifier_name + ".pdb", 'w+') #Write pbd to file
                output_metadata   = open("abYmod_metadata_" + antibody_identifier_name + ".txt", "w+") #write metadata to separate file
                output.write(retrieve_model)
                retrieve_metadata = request.urlopen(metadata_url).read()
                retrieve_metadata = str(retrieve_metadata, encoding='utf-8')
                output_metadata.write(retrieve_metadata)
                output.close()
                output_metadata.close()
                break

        else:
            print("model of ", light_chain_identifier, " could not be constructed")






    return

#*********************************************************
#*** Main program  ***
#*********************************************************

#if using wrapped sequences, must use converter script first!!!
#Run Normal_chain_identifier on input sequences and run tally on normal and irregular sequences
#Return results to display


with open(sys.argv[1]) as f:
    for line in f:
        if line[0] == ">" and re.search("L\|", line):
            light_chain_identifier = line.strip()
            light_chain = f.readline().strip()
            heavy_chain_identifier = f.readline().strip()
            heavy_chain = f.readline().strip()
            model_structure(light_chain_identifier, light_chain, heavy_chain)
