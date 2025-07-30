"""
Mutation Validator Service

This service provides a clean interface for validating RawMutation objects
and converting them into GeneMutation objects. It acts as a facade over
the more complex MutationService, providing a simpler API for the pipeline.
"""

import logging
from typing import List, Optional
from rettxmutation.models.gene_models import RawMutation, GeneMutation
from rettxmutation.services.mutation_service import MutationService
from rettxmutation.models.gene_assembly import GenomeAssembly
from rettxmutation.adapters.variant_validator_adapter import VariantValidatorNormalizationError

logger = logging.getLogger(__name__)


class MutationValidator:
    """
    Generic service for validating mutations. This provides a clean interface
    that can be easily swapped with other validation services in the future.
    """
    
    def __init__(self, mutation_service: Optional[MutationService] = None):
        """
        Initialize the mutation validator.
        
        Args:
            mutation_service: Optional MutationService instance. If None, creates a new one.
        """
        self.mutation_service = mutation_service or MutationService()

    def close(self):
        """Clean up resources."""
        if self.mutation_service:
            self.mutation_service.close()

    async def validate_mutations(
        self, 
        raw_mutations: List[RawMutation]
    ) -> List[GeneMutation]:
        """
        Validate a list of RawMutation objects and convert them to GeneMutation objects.
        
        Args:
            raw_mutations: List of RawMutation objects from the extraction agent
            genome_assembly: Target genome assembly for validation
            
        Returns:
            List[GeneMutation]: List of validated GeneMutation objects
        """
        validated_mutations = []

        for raw_mutation in raw_mutations:
            try:
                logger.info(f"Validating mutation: {raw_mutation.mutation}")

                gene_mutation = self.mutation_service.get_gene_mutation_model(
                    hgvs_string=raw_mutation.mutation,
                    gene_symbol="MECP2"
                )

                validated_mutations.append(gene_mutation)
                logger.info(f"Successfully validated mutation: {raw_mutation.mutation}")

            except VariantValidatorNormalizationError as e:
                logger.warning(f"Failed to validate mutation '{raw_mutation.mutation}': {e}")
                continue

            except Exception as e:
                logger.error(f"Unexpected error validating mutation '{raw_mutation.mutation}': {e}")
                continue

        logger.info(f"Validated {len(validated_mutations)} out of {len(raw_mutations)} mutations")
        return validated_mutations
