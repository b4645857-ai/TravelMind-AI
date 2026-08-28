"use strict";

const API_BASE = "";

let currentTrip = null;


// =====================================================
// HELPERS
// =====================================================

function $(id) {
    return document.getElementById(id);
}


function money(value) {
    return "₹" + Number(value || 0).toLocaleString("en-IN");
}


function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function showError(message) {
    $("errorBox").innerHTML = `
        <div class="error-message">
            ${escapeHtml(message)}
        </div>
    `;
}


function clearError() {
    $("errorBox").innerHTML = "";
}


function setLoading(active) {
    $("loading").classList.toggle(
        "hidden",
        !active
    );
}


function scrollToResults() {
    $("results").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// =====================================================
// QUICK TRIP
// =====================================================

function quickTrip(origin, destination) {

    $("tripInput").value =
        `5 days from ${origin} to ${destination}, ₹60000 total budget for 4 people, I love food, culture and nature`;

    $("planner").scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


// =====================================================
// BUILD TRIP
// =====================================================

async function buildTrip() {

    clearError();

    const text = $("tripInput").value.trim();

    if (!text) {
        showError(
            "Tell TravelMind a little about your trip first."
        );
        return;
    }

    const travelDate =
        $("travelDate").value || null;

    const returnDate =
        $("returnDate").value || null;

    const tripType =
        $("tripType").value || "round-trip";

    setLoading(true);

    try {

        const response = await fetch(
            `${API_BASE}/api/plan-trip`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    text: text,
                    travel_date: travelDate,
                    return_date: returnDate,
                    trip_type: tripType
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const result = await response.json();

        if (!result.ok) {
            throw new Error(
                result.error ||
                "TravelMind could not build the trip."
            );
        }

        currentTrip = result.data;

        renderTrip(currentTrip);

        $("results").classList.remove(
            "hidden"
        );

        scrollToResults();

    } catch (error) {

        console.error(error);

        showError(
            error.message ||
            "Unable to connect to TravelMind."
        );

    } finally {

        setLoading(false);
    }
}


// =====================================================
// RENDER COMPLETE TRIP
// =====================================================

function renderTrip(trip) {

    renderHeader(trip);
    renderSummary(trip);
    renderWeather(trip);
    renderSeason(trip);
    renderItinerary(trip);
    renderRecommendations(trip);
    renderBudget(trip);
    renderTransport(trip);
    renderHotels(trip);
    renderPersona(trip);
}


// =====================================================
// HEADER
// =====================================================

function renderHeader(trip) {

    $("destinationTitle").textContent =
        trip.destination || "Your destination";


    $("tripMeta").textContent =
        `${trip.days} days · ` +
        `${trip.pace || "Balanced"} pace · ` +
        `${trip.group_size || 1} traveller` +
        `${trip.group_size === 1 ? "" : "s"}`;


    const fit =
        trip.budget?.fit_percent ?? 0;

    $("fitPercent").textContent =
        `${fit}%`;
}


// =====================================================
// SUMMARY
// =====================================================

function renderSummary(trip) {

    const budget =
        trip.budget || {};

    $("estimatedTotal").textContent =
        money(budget.estimated_total);


    $("yourBudget").textContent =
        money(budget.budget);


    $("perPerson").textContent =
        money(budget.per_person);


    let stops = 0;

    (trip.itinerary || []).forEach(day => {

        (day.items || []).forEach(item => {

            if (item.type === "place") {
                stops++;
            }

        });

    });

    $("stopCount").textContent =
        stops;
}


// =====================================================
// WEATHER
// =====================================================

function renderWeather(trip) {

    const weather =
        trip.weather || {};


    if (
        weather.temperature_max !== null &&
        weather.temperature_max !== undefined
    ) {

        $("temperature").textContent =
            `${weather.temperature_max}°C`;

    } else {

        $("temperature").textContent =
            "--°C";
    }


    $("weatherDescription").textContent =
        weather.condition ||
        "Seasonal conditions";


    $("rainChance").textContent =
        weather.rain_chance !== null &&
        weather.rain_chance !== undefined
            ? `${weather.rain_chance}%`
            : "--%";


    $("weatherSource").textContent =
        weather.source ||
        "TravelMind weather estimate";
}


// =====================================================
// SEASON
// =====================================================

function renderSeason(trip) {

    $("bestMonth").textContent =
        trip.best_month ||
        "Seasonal guidance";


    $("seasonStatus").textContent =
        trip.season_status ||
        "Check local conditions before departure.";


    $("selectedDate").textContent =
        trip.travel_date ||
        "Flexible date";
}


// =====================================================
// ITINERARY
// =====================================================

function renderItinerary(trip) {

    const container =
        $("itineraryContainer");


    container.innerHTML = "";


    const itinerary =
        trip.itinerary || [];


    if (!itinerary.length) {

        container.innerHTML = `
            <div class="empty-state">
                No itinerary stops were generated.
            </div>
        `;

        return;
    }


    itinerary.forEach(day => {

        const wrapper =
            document.createElement("div");

        wrapper.className =
            "day-block";


        const items =
            (day.items || [])
                .map(item => {

                    const isPlace =
                        item.type === "place";


                    const weatherNote =
                        item.weather_note
                            ? `
                                <div class="weather-warning">
                                    ${escapeHtml(
                                        item.weather_note
                                    )}
                                </div>
                              `
                            : "";


                    return `
                        <div class="timeline-item">

                            <div class="timeline-time">
                                ${escapeHtml(
                                    item.time
                                )}
                            </div>

                            <div class="timeline-dot">
                                ${isPlace ? "✦" : "•"}
                            </div>

                            <div class="timeline-content">

                                <div class="timeline-type">
                                    ${escapeHtml(
                                        item.category ||
                                        ""
                                    )}
                                </div>

                                <h4>
                                    ${escapeHtml(
                                        item.name
                                    )}
                                </h4>

                                <p>
                                    ${escapeHtml(
                                        item.description ||
                                        ""
                                    )}
                                </p>

                                ${
                                    isPlace &&
                                    item.rating
                                        ? `
                                            <span class="rating">
                                                ★ ${item.rating}
                                            </span>
                                          `
                                        : ""
                                }

                                <span class="item-cost">
                                    ${money(
                                        item.cost || 0
                                    )}
                                </span>

                                ${weatherNote}

                            </div>

                        </div>
                    `;

                })
                .join("");


        wrapper.innerHTML = `

            <div class="day-heading">

                <div class="day-number">
                    ${day.day}
                </div>

                <div>

                    <span>
                        DAY ${day.day}
                    </span>

                    <h3>
                        ${escapeHtml(
                            day.title || "Explore"
                        )}
                    </h3>

                </div>

            </div>

            <div class="timeline">
                ${items}
            </div>
        `;


        container.appendChild(wrapper);
    });
}


// =====================================================
// RECOMMENDATIONS
// =====================================================

function renderRecommendations(trip) {

    const grid =
        $("recommendationGrid");


    grid.innerHTML = "";


    const recommendations =
        trip.recommendations || [];


    if (!recommendations.length) {

        grid.innerHTML = `
            <div class="empty-state">
                No recommendations available.
            </div>
        `;

        return;
    }


    recommendations.forEach(place => {

        const card =
            document.createElement("article");

        card.className =
            "recommendation-card";


        card.innerHTML = `

            <div class="recommendation-image">

                <img
                    src="${escapeHtml(
                        place.image || ""
                    )}"
                    alt="${escapeHtml(
                        place.name
                    )}"
                    loading="lazy"
                    onerror="this.style.display='none'"
                >

            </div>


            <div class="recommendation-body">

                <div class="recommendation-category">
                    ${escapeHtml(
                        place.category || ""
                    )}
                </div>

                <h3>
                    ${escapeHtml(
                        place.name
                    )}
                </h3>

                <p>
                    ${escapeHtml(
                        place.description || ""
                    )}
                </p>


                <div class="recommendation-footer">

                    <span>
                        ★ ${place.rating || "--"}
                    </span>

                    <span>
                        ${
                            place.cost
                                ? money(place.cost)
                                : "Free"
                        }
                    </span>

                </div>

            </div>
        `;


        grid.appendChild(card);
    });
}


// =====================================================
// BUDGET
// =====================================================

function renderBudget(trip) {

    const budget =
        trip.budget || {};


    const categories =
        budget.categories || {};


    const total =
        Math.max(
            Number(budget.estimated_total || 0),
            1
        );


    const stay =
        Number(categories.stay || 0);

    const food =
        Number(categories.food || 0);

    const activities =
        Number(categories.activities || 0);

    const transport =
        Number(categories.transport || 0);

    const local =
        Number(categories.local_transport || 0);


    setText(
        "stayAmount",
        money(stay)
    );

    setText(
        "foodAmount",
        money(food)
    );

    setText(
        "activityAmount",
        money(activities)
    );

    setText(
        "transportAmount",
        money(transport)
    );

    setText(
        "localAmount",
        money(local)
    );


    setText(
        "stayPercent",
        `${percent(stay, total)}%`
    );

    setText(
        "foodPercent",
        `${percent(food, total)}%`
    );

    setText(
        "activityPercent",
        `${percent(activities, total)}%`
    );

    setText(
        "transportPercent",
        `${percent(transport, total)}%`
    );

    setText(
        "localPercent",
        `${percent(local, total)}%`
    );


    setText(
        "budgetCenter",
        money(budget.estimated_total)
    );


    const donut =
        $("budgetDonut");


    const stayPct =
        (stay / total) * 100;

    const foodPct =
        (food / total) * 100;

    const activityPct =
        (activities / total) * 100;

    const transportPct =
        (transport / total) * 100;


    const first =
        stayPct;

    const second =
        first + foodPct;

    const third =
        second + activityPct;

    const fourth =
        third + transportPct;


    donut.style.background =
        `conic-gradient(
            var(--budget-stay) 0 ${first}%,
            var(--budget-food) ${first}% ${second}%,
            var(--budget-activity) ${second}% ${third}%,
            var(--budget-transport) ${third}% ${fourth}%,
            var(--budget-local) ${fourth}% 100%
        )`;
}


// =====================================================
// TRANSPORT
// =====================================================

function renderTransport(trip) {

    const grid =
        $("transportGrid");


    grid.innerHTML = "";


    const options =
        trip.transport || [];


    if (!options.length) {

        grid.innerHTML = `
            <div class="empty-state">
                No intercity transport route was specified.
            </div>
        `;

        return;
    }


    const selected =
        trip.selected_transport?.mode;


    options.forEach(option => {

        const card =
            document.createElement("div");

        const isSelected =
            option.mode === selected;


        card.className =
            `transport-card ${
                isSelected
                    ? "selected"
                    : ""
            }`;


        card.innerHTML = `

            ${
                option.label
                    ? `
                        <div class="transport-label">
                            ${escapeHtml(
                                option.label
                            )}
                        </div>
                      `
                    : ""
            }


            <div class="transport-icon">
                ${option.icon || "•"}
            </div>


            <div class="transport-main">

                <h3>
                    ${escapeHtml(
                        option.mode
                    )}
                </h3>

                <span>
                    ${escapeHtml(
                        option.duration ||
                        ""
                    )}
                </span>

                <small>
                    ${escapeHtml(
                        option.price_type ||
                        "Estimated"
                    )}
                </small>

            </div>


            <div class="transport-price">

                <strong>
                    ${money(
                        option.estimated_total
                    )}
                </strong>

                <span>
                    group total
                </span>

            </div>

        `;


        grid.appendChild(card);
    });
}


// =====================================================
// HOTELS
// =====================================================

function renderHotels(trip) {

    const grid =
        $("hotelGrid");


    grid.innerHTML = "";


    const hotels =
        trip.hotels || [];


    const selected =
        trip.selected_hotel?.name;


    if (!hotels.length) {

        grid.innerHTML = `
            <div class="empty-state">
                No accommodation options available.
            </div>
        `;

        return;
    }


    hotels.forEach(hotel => {

        const card =
            document.createElement("article");


        const isSelected =
            hotel.name === selected;


        card.className =
            `hotel-card ${
                isSelected
                    ? "selected"
                    : ""
            }`;


        card.innerHTML = `

            <div class="hotel-image">

                <img
                    src="${escapeHtml(
                        hotel.image || ""
                    )}"
                    alt="${escapeHtml(
                        hotel.name
                    )}"
                    loading="lazy"
                    onerror="this.style.display='none'"
                >

            </div>


            <div class="hotel-body">

                ${
                    isSelected
                        ? `
                            <span class="selected-badge">
                                USED IN PLAN
                            </span>
                          `
                        : ""
                }


                <div class="hotel-tier">
                    ${escapeHtml(
                        hotel.tier || ""
                    )}
                </div>


                <h3>
                    ${escapeHtml(
                        hotel.name
                    )}
                </h3>


                <p>
                    ${escapeHtml(
                        hotel.area || ""
                    )}
                </p>


                <div class="hotel-bottom">

                    <span>
                        ★ ${hotel.rating || "--"}
                    </span>

                    <strong>
                        ${money(
                            hotel.nightly
                        )}
                        <small>
                            / night
                        </small>
                    </strong>

                </div>

            </div>
        `;


        grid.appendChild(card);
    });
}


// =====================================================
// PERSONA
// =====================================================

function renderPersona(trip) {

    const persona =
        trip.travel_persona ||
        "Balanced Explorer";


    $("personaText").textContent =
        `${persona} · ` +
        `${trip.interests?.join(", ") || "local experiences"}`;
}


// =====================================================
// ADAPTIVE REPLANNING
// =====================================================

async function adaptTrip() {

    if (!currentTrip) {

        showError(
            "Build a trip before adapting it."
        );

        return;
    }


    const change =
        $("adaptInput").value.trim();


    if (!change) {

        showError(
            "Tell TravelMind what changed."
        );

        return;
    }


    clearError();

    setLoading(true);


    try {

        const response = await fetch(
            `${API_BASE}/api/adapt-trip`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    trip: currentTrip,
                    change: change
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const result =
            await response.json();


        if (!result.ok) {

            throw new Error(
                result.error ||
                "Unable to adapt the trip."
            );
        }


        currentTrip =
            result.data;


        renderTrip(
            currentTrip
        );


        $("adaptInput").value = "";


        const message =
            $("saveMessage");


        if (message) {

            message.textContent =
                "Trip successfully recalculated around your new constraint.";

        }


        scrollToResults();

    } catch (error) {

        console.error(error);

        showError(
            error.message ||
            "Could not re-plan the trip."
        );

    } finally {

        setLoading(false);
    }
}


// =====================================================
// SAVE TRIP
// =====================================================

async function saveTrip() {

    if (!currentTrip) {

        showError(
            "Build a trip before saving it."
        );

        return;
    }


    const button =
        document.querySelector(
            ".save-btn"
        );


    const originalText =
        button
            ? button.textContent
            : "";


    try {

        if (button) {
            button.disabled = true;
            button.textContent =
                "Saving...";
        }


        const response =
            await fetch(
                `${API_BASE}/api/save-trip`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        trip: currentTrip
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const result =
            await response.json();


        if (!result.ok) {

            throw new Error(
                result.error ||
                "Unable to save trip."
            );
        }


        $("saveMessage").innerHTML =
            `Saved successfully. Your trip ID is <strong>${escapeHtml(
                result.trip_id
            )}</strong>. Keep this ID to re-access the plan.`;


    } catch (error) {

        console.error(error);

        showError(
            error.message ||
            "Could not save the trip."
        );

    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                originalText ||
                "Save this trip →";
        }
    }
}


// =====================================================
// UTILITY FUNCTIONS
// =====================================================

function setText(id, value) {

    const element =
        $(id);

    if (element) {
        element.textContent =
            value;
    }
}


function percent(value, total) {

    if (!total) {
        return 0;
    }

    return Math.round(
        (value / total) * 100
    );
}


// =====================================================
// DATE INITIALIZATION
// =====================================================

function initializeDates() {

    const today =
        new Date();


    const departure =
        new Date(today);

    departure.setDate(
        today.getDate() + 14
    );


    const returnDate =
        new Date(departure);

    returnDate.setDate(
        departure.getDate() + 4
    );


    $("travelDate").value =
        formatDate(departure);


    $("returnDate").value =
        formatDate(returnDate);


    $("travelDate").addEventListener(
        "change",
        updateReturnMinimum
    );


    updateReturnMinimum();
}


function updateReturnMinimum() {

    const departure =
        $("travelDate").value;


    if (departure) {

        $("returnDate").min =
            departure;

        if (
            $("returnDate").value &&
            $("returnDate").value < departure
        ) {

            $("returnDate").value =
                departure;
        }
    }
}


function formatDate(date) {

    const year =
        date.getFullYear();

    const month =
        String(
            date.getMonth() + 1
        ).padStart(2, "0");

    const day =
        String(
            date.getDate()
        ).padStart(2, "0");


    return `${year}-${month}-${day}`;
}


// =====================================================
// KEYBOARD SHORTCUT
// =====================================================

document.addEventListener(
    "keydown",
    event => {

        if (
            event.ctrlKey &&
            event.key === "Enter"
        ) {

            event.preventDefault();

            buildTrip();
        }
    }
);


// =====================================================
// STARTUP
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeDates();

        const input =
            $("tripInput");


        if (input) {

            input.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter" &&
                        event.ctrlKey
                    ) {

                        event.preventDefault();

                        buildTrip();
                    }

                }
            );
        }

    }
);