import gradio as gr
import requests
import datetime

API = "http://127.0.0.1:8080"

def submit_usage(device_id, energy):
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    payload = {
        "timestamp": ts,
        "energy_kwh": energy,
        "device_id": device_id
    }
    try:
        r = requests.post(f"{API}/api/energy/usage", json=payload)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def show_history(limit):
    try:
        r = requests.get(f"{API}/api/energy/usage", params={"limit": limit})
        data = r.json()
        return [
            [d["timestamp"], d["device_id"], d["energy_kwh"]] for d in data
        ]
    except Exception as e:
        return [["Error", "", str(e)]]

def get_advice(hour):
    try:
        r = requests.get(f"{API}/api/energy/optimize", params={"hour": hour})
        return r.json()
    except Exception as e:
        return {"error": str(e)}

with gr.Blocks() as demo:
    gr.Markdown("## Smart Home Energy Management System")

    with gr.Tab("Record Usage"):
        with gr.Row():
            dev = gr.Textbox(label="Device ID", value="METER_MAIN")
            ekwh = gr.Slider(0.0, 10.0, value=1.0, label="Energy (kWh)")
        btn = gr.Button("Submit Usage")
        out1 = gr.JSON()
        btn.click(submit_usage, inputs=[dev, ekwh], outputs=out1)

    with gr.Tab("View History"):
        lim = gr.Slider(1, 50, value=10, label="Show Last N Records")
        tbl = gr.Dataframe(headers=["Timestamp", "Device ID", "Energy (kWh)"], row_count=10)
        lim.change(fn=show_history, inputs=lim, outputs=tbl)

    with gr.Tab("Optimization Advice"):
        hr = gr.Slider(0, 23, value=datetime.datetime.now(datetime.UTC).hour, label="Hour of Day")
        adv = gr.JSON()
        hr.change(fn=get_advice, inputs=hr, outputs=adv)

demo.launch()

