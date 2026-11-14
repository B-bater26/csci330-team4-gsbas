// Determine math and output
function generate_outputs(census_query) {
    let population_output = 0;
    let age_median_total = 0.0;
    let age_weight = 0.0;
    let male_pop = 0;
    let female_pop = 0;
    let income_median_total = 0.0;
    let income_weight = 0.0;
    let vacant = 0;
    let home_owners = 0;
    let renters = 0;
    let hv_total = 0.0;
    let hv_weight = 0.0;
    let pop_25 = 0.0;
    let education_total = 0;
    let employed_total = 0;
    let unemployed_total = 0;
    let workforce = 0;
    let workers = 0;
    let drivers_total = 0;
    let transit_total = 0;
    let households = 0;
    let internet_h = 0;
    let internet_total = 0;
    for (const stats of Object.values(census_query)) {
        // Population - Sum
        if (stats.B01003_001E) {
            population_output += stats.B01003_001E;
            // Age - Weighted
        } if (stats.B01002_001E) {
            age_median_total += stats.B01002_001E * stats.B01003_001E;
            age_weight += stats.B01003_001E;
        }
        // Sex - Sum -> Percent
        if (stats.B01001_002E) {
            male_pop += stats.B01001_002E;
        } if (stats.B01001_026E) {
            female_pop += stats.B01001_026E;
        }
        // Median Income - Weighted
        if (stats.B19013_001E) {
            income_median_total += stats.B19013_001E * stats.B01003_001E;
            income_weight += stats.B01003_001E;
        }
        // Vacant Housing - Sum
        if (stats.B25002_003E) {
            vacant += stats.B25002_003E;
        }
        // Home Owners - Sum
        if (stats.B25003_002E) {
            home_owners += stats.B25003_002E;
        }
        // Renters - Sum
        if (stats.B25003_003E) {
            renters += stats.B25003_003E;
        }
        // Home Value - Weighted
        if (stats.B25077_001E) {
            hv_total += stats.B25077_001E * stats.B25003_002E;
            hv_weight += stats.B25003_002E;
        }
        // Education - Sum / Population
        if (stats.B15003_001E) {
            pop_25 += stats.B15003_001E;
        } if (stats.B15003_022E) {
            education_total += stats.B15003_022E;
        } if (stats.B15003_023E) {
            education_total += stats.B15003_023E;
        } if (stats.B15003_024E) {
            education_total += stats.B15003_024E;
        } if (stats.B15003_025E) {
            education_total += stats.B15003_025E;
        }
        // Workforce - Sum
        if (stats.B23025_003E) {
            workforce += stats.B23025_003E;
        }
        // Employed - Percent (4/3)
        if (stats.B23025_004E) {
            employed_total += stats.B23025_004E;
        }
        // Unemployed - Percent (5/3) 
        if (stats.B23025_005E) {
            unemployed_total += stats.B23025_005E;
        }
        // Commuters - (Sum / Workers), (Sum / Workers)
        if (stats.B08301_001E) {
            workers += stats.B08301_001E;
        } if (stats.B08301_003E) {
            drivers_total += stats.B08301_003E;
        } if (stats.B08301_010E) {
            transit_total += stats.B08301_010E;
        }
        // Internet - Sum/Pop
        if (stats.B11001_001E) {
            households += stats.B11001_001E;
        } if (stats.B28002_001E) {
            internet_h += stats.B28002_001E;
        } if (stats.B28002_002E) {
            internet_total += stats.B28002_002E;
        }



    }

    // Math
    const male_pop_total = male_pop > 0 ? male_pop / (male_pop + female_pop) * 100 : null;
    const female_pop_total = female_pop > 0 ? female_pop / (male_pop + female_pop) * 100 : null;
    const median_age = age_weight > 0 ? age_median_total / age_weight : null;
    const median_income = income_weight > 0 ? income_median_total / income_weight : null;
    const home_value = hv_weight > 0 ? hv_total / hv_weight : null;
    const educated_pop = pop_25 > 0 ? education_total / pop_25 * 100 : null;
    const employed = population_output > 0 ? employed_total / workforce * 100 : null;
    const unemployed = population_output > 0 ? unemployed_total / workforce * 100 : null;
    const commuter_workers = workers > 0 ? drivers_total / workers * 100 : null;
    const transit_workers = workers > 0 ? transit_total / workers * 100 : null;
    const internet_full = internet_h > 0 ? internet_total / internet_h * 100 : null;

    return {
        "Population": population_output,
        "Households": households,
        "Sex": {
            "Male Percentage": male_pop_total,
            "Female Percentage": female_pop_total
        },
        "Median Age": median_age,
        "Median Household Income": median_income,
        "Vacant Homes": vacant,
        "Home Owners": home_owners,
        "Renters": renters,
        "Median Home Value": home_value,
        "Educated (% over 25)": educated_pop,
        "Employed Percentage": employed,
        "Unemployed Percentage": unemployed,
        "commuters": {
            "Commuters Who Drive (%)": commuter_workers,
            "Commuters Who Use Public Transit (%)": transit_workers
        },
        "Households with Internet (%)": internet_full

    }



}

// Display Outputs
function display_outputs(outputs, containerId = "outputs-container") {
    const output_container = document.getElementById(containerId);
    let cards = ""
    Object.entries(outputs).forEach(([key, value]) => {
        if (value && !(typeof value === 'object')) {
            cards += `
            <div class="output-card">
                <h1>${key}</h2>
                <h2>${Math.round(value)}</h2>
            </div>
            `
        } else if (value && (typeof value === 'object')) {
            Object.entries(value).forEach(([subKey, subValue]) => {
                if (subValue) {
                cards += `
                <div class="output-card">
                    <h1>${subKey}</h2>
                    <h2>${Math.round(subValue)}</h2>
                </div>
                `
                }
            })
        }

    })

    output_container.innerHTML = cards;


}
