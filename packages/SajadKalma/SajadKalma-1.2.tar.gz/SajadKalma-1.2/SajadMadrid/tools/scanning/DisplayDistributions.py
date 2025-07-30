# من تطوير Sajad @f_g_d_6


""" Display the Distributions installed. """

from SajadMadrid.utils.Distributions import (
    getDistributionInstallerName,
    getDistributionName,
    getDistributions,
    getDistributionVersion,
)


def displayDistributions():
    for distributions in getDistributions().values():
        for distribution in distributions:
            distribution_name = getDistributionName(distribution)
            #            print(distribution_name, distribution)
            print(
                distribution_name,
                getDistributionVersion(distribution),
                getDistributionInstallerName(distribution_name=distribution_name),
            )



