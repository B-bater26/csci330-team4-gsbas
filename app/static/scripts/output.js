// Determine math and output
function generate_outputs(census_query) {
    let population_output = 0;
    let age_median_total = 0.0;
    let age_weighted = 0.0;
    for (const stats of Object.values(census_query)) {
        // Population
        if (stats.B01003_001E) {
            population_output += stats.B01003_001E;
        // Age
        } if (stats.B01002_001E) {
            age_median_total += stats.B01002_001E;
            age_weighted += population_output;
        }
    }

    console.log(population_output, age_weighted)



}

