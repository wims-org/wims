// var g_locale = "{{ g.locale|tojson }}";

document.addEventListener("DOMContentLoaded", function () {
    var targetContainer = document.getElementById("target_div");
    const current_url = new URL(window.location.toLocaleString());
    const reader_id = current_url.searchParams.get("reader");
    var eventSource = new EventSource("/stream?reader=" + reader_id);
    /*
     * This will listen only for events
     * similar to the following:
     *
     * event: REDIRECT
     * data: useful data
     * id: some-id
     */
    eventSource.addEventListener("REDIRECT", (e) => {
        data = JSON.parse(e.data.replace(/'/g, '"'));
        console.log(e.data, data["reader_id"], data.rfid, "/item/" + data.rfid + "?reader=" + data.reader_id);
        targetContainer.innerHTML = e.data;
        // window.location.href = "/item?reader=
        window.location.replace("/item/" + data.rfid + "?reader=" + data.reader_id);
    });

    /*
     * Similarly, this will listen for events
     * with the field `event: update`
     */
    eventSource.addEventListener("update", (e) => {
        console.log(e.data);
    });

    /*
     * The event "message" is a special case, as it
     * will capture events without an event field
     * as well as events that have the specific type
     * `event: message` It will not trigger on any
     * other event type.
     */
    eventSource.addEventListener("message", (e) => {
        console.log(e.data);
    });
});
