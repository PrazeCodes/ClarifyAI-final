import { useState } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { toast } from "sonner";
import { Upload, MessageSquare, LogOut, FileText, Sparkles } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ onLogout }) {
  const [askAIQuestion, setAskAIQuestion] = useState("");
  const [askAIAnswer, setAskAIAnswer] = useState("");
  const [askAILoading, setAskAILoading] = useState(false);

  const [pdfFile, setPdfFile] = useState(null);
  const [pdfQuestion, setPdfQuestion] = useState("");
  const [pdfAnswer, setPdfAnswer] = useState("");
  const [pdfLoading, setPdfLoading] = useState(false);

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const token = localStorage.getItem('token');

  const handleAskAI = async (e) => {
    e.preventDefault();
    if (!askAIQuestion.trim()) {
      toast.error("Please enter a question");
      return;
    }

    setAskAILoading(true);
    try {
      const response = await axios.post(
        `${API}/ask-ai`,
        { question: askAIQuestion },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAskAIAnswer(response.data.answer);
      toast.success("Answer received!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to get answer");
    } finally {
      setAskAILoading(false);
    }
  };

  const handleChatWithPDF = async (e) => {
    e.preventDefault();
    if (!pdfFile) {
      toast.error("Please upload a PDF file");
      return;
    }
    if (!pdfQuestion.trim()) {
      toast.error("Please enter a question");
      return;
    }

    setPdfLoading(true);
    try {
      const formData = new FormData();
      formData.append('pdf_file', pdfFile);
      formData.append('question', pdfQuestion);

      const response = await axios.post(
        `${API}/chat-pdf`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setPdfAnswer(response.data.answer);
      toast.success("Answer received!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to process PDF");
    } finally {
      setPdfLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      setPdfAnswer("");
      toast.success(`File "${file.name}" uploaded successfully`);
    } else {
      toast.error("Please upload a valid PDF file");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold" style={{ fontFamily: 'Space Grotesk, sans-serif', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }} data-testid="dashboard-title">
                ClarifyAI
              </h1>
              <p className="text-sm text-slate-600 mt-1" data-testid="dashboard-welcome">Welcome back, {user.username}!</p>
            </div>
            <Button
              onClick={onLogout}
              variant="outline"
              className="flex items-center gap-2 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition-colors"
              data-testid="logout-button"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="chat-pdf" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-md mx-auto mb-8 h-12 bg-white shadow-md" data-testid="dashboard-tabs">
            <TabsTrigger value="chat-pdf" className="text-base font-medium" data-testid="chat-pdf-tab">
              <FileText className="h-4 w-4 mr-2" />
              Chat with PDF
            </TabsTrigger>
            <TabsTrigger value="ask-ai" className="text-base font-medium" data-testid="ask-ai-tab">
              <Sparkles className="h-4 w-4 mr-2" />
              Ask AI
            </TabsTrigger>
          </TabsList>

          {/* Chat with PDF Tab */}
          <TabsContent value="chat-pdf" data-testid="chat-pdf-content">
            <Card className="max-w-4xl mx-auto shadow-lg border-0 bg-white/90 backdrop-blur">
              <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-indigo-50">
                <CardTitle className="flex items-center gap-2 text-2xl" data-testid="chat-pdf-title">
                  <FileText className="h-6 w-6 text-purple-600" />
                  Chat with PDF
                </CardTitle>
                <CardDescription className="text-base" data-testid="chat-pdf-description">
                  Upload a PDF document and ask questions about its content
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <form onSubmit={handleChatWithPDF} className="space-y-6">
                  {/* File Upload */}
                  <div className="space-y-2">
                    <Label htmlFor="pdf-upload" className="text-base font-medium">Upload PDF Document</Label>
                    <div className="flex items-center gap-4">
                      <label
                        htmlFor="pdf-upload"
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-8 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-purple-500 hover:bg-purple-50/50 transition-all"
                        data-testid="pdf-upload-label"
                      >
                        <Upload className="h-5 w-5 text-slate-400" />
                        <span className="text-slate-600">
                          {pdfFile ? pdfFile.name : "Click to upload PDF"}
                        </span>
                      </label>
                      <input
                        id="pdf-upload"
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="hidden"
                        data-testid="pdf-upload-input"
                      />
                    </div>
                  </div>

                  {/* Question Input */}
                  <div className="space-y-2">
                    <Label htmlFor="pdf-question" className="text-base font-medium">Your Question</Label>
                    <Textarea
                      id="pdf-question"
                      placeholder="Ask anything about the PDF content..."
                      value={pdfQuestion}
                      onChange={(e) => setPdfQuestion(e.target.value)}
                      rows={4}
                      className="resize-none"
                      data-testid="pdf-question-input"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={pdfLoading || !pdfFile}
                    className="w-full h-12 text-base font-medium"
                    style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                    data-testid="pdf-submit-button"
                  >
                    {pdfLoading ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                        Processing...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Get Answer
                      </span>
                    )}
                  </Button>
                </form>

                {/* Answer Display */}
                {pdfAnswer && (
                  <div className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg border border-purple-200" data-testid="pdf-answer-box">
                    <h3 className="font-semibold text-lg mb-3 text-purple-900">Answer:</h3>
                    <p className="text-slate-700 whitespace-pre-wrap leading-relaxed" data-testid="pdf-answer-text">{pdfAnswer}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Ask AI Tab */}
          <TabsContent value="ask-ai" data-testid="ask-ai-content">
            <Card className="max-w-4xl mx-auto shadow-lg border-0 bg-white/90 backdrop-blur">
              <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                <CardTitle className="flex items-center gap-2 text-2xl" data-testid="ask-ai-title">
                  <Sparkles className="h-6 w-6 text-blue-600" />
                  Ask AI
                </CardTitle>
                <CardDescription className="text-base" data-testid="ask-ai-description">
                  Ask any question and get intelligent answers powered by Gemini AI
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <form onSubmit={handleAskAI} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="ask-question" className="text-base font-medium">Your Question</Label>
                    <Textarea
                      id="ask-question"
                      placeholder="Ask me anything..."
                      value={askAIQuestion}
                      onChange={(e) => setAskAIQuestion(e.target.value)}
                      rows={4}
                      className="resize-none"
                      data-testid="ask-ai-question-input"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={askAILoading}
                    className="w-full h-12 text-base font-medium"
                    style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                    data-testid="ask-ai-submit-button"
                  >
                    {askAILoading ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                        Thinking...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4" />
                        Ask AI
                      </span>
                    )}
                  </Button>
                </form>

                {/* Answer Display */}
                {askAIAnswer && (
                  <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200" data-testid="ask-ai-answer-box">
                    <h3 className="font-semibold text-lg mb-3 text-blue-900">Answer:</h3>
                    <p className="text-slate-700 whitespace-pre-wrap leading-relaxed" data-testid="ask-ai-answer-text">{askAIAnswer}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
