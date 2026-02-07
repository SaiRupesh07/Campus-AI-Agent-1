const BASE_URL = process.env.REACT_APP_API_URL;

export const chatAPI = async (message, session_id="default") => {
  try {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id,
      }),
    });

    return await res.json();
  } catch (err) {
    console.error("Backend connection error:", err);
  }
};
