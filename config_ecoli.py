 # -*- coding: utf-8 -*-
config = {
        'data_process':
                {
                        'gene_expression_maximum_level': 10.0,
                        'gene_expression_minimum_level': -10.0,
                        'phenotype_scale_factor': 1.0,
                },
        'model_construct':
                {
                        'gene_protein_connection_mask': 'E_coli_model/iJO1366_gene_protein_rule.csv',
                        'protein_phenotype_connection_mask': 'E_coli_model/iJO1366_protein_phenotype_rule_growth.csv',

                },
        'unsupervised':
                {
                        'gene': 'E_coli_model/iJO1366_unsupervised_transcriptomics.csv',
                        'epochs': 200,
                        'batch_size': 5000,
                        'save_to': 'E_coli_model/your_iJO1366_unsupervised_result.csv',
                },

        'supervised':
                {
                        'gene': 'E_coli_model/iJO1366_supervised_transcriptomics.csv',
                        'phenotype': 'E_coli_model/iJO1366_supervised_phenotype_growth.csv',
                        'epochs': 100000,
                        'converge_delta': 0.0001,
                        'indices': 'E_coli_model/iJO1366_phenotype_indices.txt',
                        'save_to': 'E_coli_model/your_iJO1366_supervised_result.csv',
                        'model_save_to': 'E_coli_model/iJO1366_graphic_model.ckpt',
                },
        'model_input':
                {
                        'gene': 'E_coli_model/iJO1366_supervised_transcriptomics.csv',
                        'model_load_from': 'E_coli_model/iJO1366_graphic_model.ckpt',
                        'result_save_to': 'E_coli_model/your_iJO1366_prediction_result.csv',
                },
        'model_preparation':
                {
                        'input_model': 'E_coli_model/iJO1366.xml',
                        'available_phenotypes': 'E_coli_model/iJO1366_pheno_names.txt',
                        'gene_protein_connection_mask': 'E_coli_model/iJO1366_gene_protein_rule.csv',
                        'protein_phenotype_connection_mask': 'E_coli_model/iJO1366_protein_phenotype_rule.csv ',
                        'phenotype_indices': 'E_coli_model/iJO1366_phenotype_indices.txt',

                },

}

