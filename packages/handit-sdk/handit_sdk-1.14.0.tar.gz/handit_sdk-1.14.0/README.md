# Handit.AI Python SDK Documentation

AI model deployment and management often fall short of delivering the expected business outcomes, with up to 80% of AI projects never scaling beyond pilot stages. To address this challenge, **Handit.AI** provides a comprehensive AI Lifecycle Management Platform that ensures AI models are continuously aligned with business goals and KPIs.

The **Handit.AI Python SDK** is designed to streamline the process of monitoring, tracking, and optimizing AI models in production. With features for automated and manual data capture, seamless integration, and real-time performance insights, this SDK empowers businesses to maintain the effectiveness and reliability of their AI models.

---

### **What Handit.AI Python SDK Offers**

1. **Continuous Monitoring of AI Models**  
   Detect performance degradation and data drift in real-time, ensuring your models remain accurate and reliable.

2. **Automated Data Capture**  
   Automatically track model inputs and outputs for HTTP requests using tools like `requests`, streamlining the tracking process without requiring manual intervention.

3. **Business KPI Alignment**  
   Capture and monitor AI model inputs and outputs to align model performance with your business’s strategic objectives.

4. **Seamless Integration**  
   Easily integrate into your existing Python-based AI workflows, including popular frameworks like PyTorch, TensorFlow, and Scikit-learn.

5. **Custom AI Model Tracking**  
   Manually track specific model events to ensure critical data is never missed, providing a holistic view of AI model performance.

---

### **Why Use Handit.AI Python SDK?**

Handit.AI Python SDK addresses the critical issues AI projects face, such as the disconnect between model performance and business goals, performance degradation, and lack of continuous optimization. By integrating our tracking tools, your AI models become transparent, measurable, and continuously optimized, helping you achieve long-term success.

#### **Key Benefits:**

- **Improved AI ROI**  
  Directly connect model performance to business outcomes, ensuring that your AI initiatives deliver the value they promise.

- **Proactive Issue Prevention**  
  Identify performance issues and data drift early, allowing for rapid optimization.

- **Reduced Time to Market**  
  Automate much of the manual work required to monitor and optimize AI models, accelerating the deployment process.

---

### **Installation**

Install the SDK from PyPI:

```bash
pip install handit-sdk
```

---

### **Getting Started**

#### **1. Configure the SDK**

Set up the SDK with your API key and tracking server URL (optional):

```python
from handit_tracker import HanditTracker

tracker = HanditTracker()
tracker.config(api_key="your-api-key", tracking_url="https://your-custom-tracking-url.com")
```

---

#### **2. Automatically Intercept HTTP Requests**

Wrap your `requests` library calls to automatically capture data:

```python
import requests
from handit_tracker import HanditTracker

tracker = HanditTracker()
tracker.config(api_key="your-api-key")

# Intercept requests
@tracker.intercept_requests
def make_request(url, **kwargs):
    return requests.get(url, **kwargs)

response = make_request("https://example.com/api/data")
```

---

#### **3. Manually Capture Model Data**

Manually capture model input and output data for specific events:

```python
tracker.capture_model(
    model_id="model-slug",
    request_body={"input_key": "input_value"},
    response_body={"output_key": "output_value"}
)
```

---

### **Advanced Features**

1. **Update Tracked URLs Dynamically**  
   The SDK automatically fetches the list of URLs to track from the configured tracking server.

2. **Customizable Model ID Extraction**  
   Adjust the logic for extracting `model_id` from the URL based on your API's structure.

3. **Error Handling and Reporting**  
   Automatically report errors and failed API responses for improved visibility into issues.

---

### **Contributing**

We welcome contributions! Please visit the [GitHub repository](https://github.com/yourusername/handit-sdk) to report issues or submit pull requests.

---

### **License**

This project is licensed under the MIT License. See the [LICENSE](https://github.com/yourusername/handit-sdk/blob/main/LICENSE) file for details.  

