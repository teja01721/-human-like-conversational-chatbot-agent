export default async function handler(req, res) {
  if (req.method === "POST") {
    const { message } = req.body;
    // Replace this with your chatbot logic
    const reply = `You said: ${message}`;
    res.status(200).json({ reply });
  } else {
    res.status(405).send("Method Not Allowed");
  }
}
