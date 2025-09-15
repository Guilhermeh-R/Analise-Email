"use client";
import React, { useState, useEffect } from "react";
import "./globals.css";

export default function Home() {
  const [sugestionEmail, setSugestionEmail] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setSugestionEmail(null);
    setError(null);
    if (file) submitFile(file);
  };

  const submitFile = async (file: File) => {
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://analise-email.onrender.com/process", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setSugestionEmail(data);
        showToast("Arquivo processado com sucesso!", "success");
      } else {
        setError("Erro ao processar o arquivo.");
        showToast("Erro ao processar o arquivo.", "error");
      }
    } catch (err) {
      setError("Erro na requisição. Tente novamente.");
      showToast("Erro na requisição. Tente novamente.", "error");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitText = async () => {
    setLoading(true);
    setSugestionEmail(null);
    setError(null);

    const textInput = (document.getElementById("textInput") as HTMLTextAreaElement).value;

    if (!textInput.trim()) {
      setError("Digite algum texto para análise.");
      showToast("Digite algum texto para análise.", "error");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("https://analise-email.onrender.com/process_Text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textInput }),
      });

      if (response.ok) {
        const data = await response.json();
        setSugestionEmail(data);
        showToast("Texto processado com sucesso!", "success");
      } else {
        setError("Erro ao processar o texto.");
        showToast("Erro ao processar o texto.", "error");
      }
    } catch (err) {
      setError("Erro na requisição. Tente novamente.");
      showToast("Erro na requisição. Tente novamente.", "error");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="font-sans min-h-screen p-8 sm:p-20 grid grid-rows-[auto_1fr_auto] gap-12 justify-items-center">
      <h1 className="text-5xl font-bold text-center bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 bg-clip-text text-transparent animate-gradient">
        Análise de Email com IA
      </h1>

      <div className="flex flex-col gap-8 w-full max-w-4xl">
        {/* Upload */}
        <div className="p-[3px] rounded-xl bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 animate-gradient">
          <div className="bg-gray-900 rounded-xl p-6 flex flex-col items-center">
            <input
              type="file"
              id="fileInput"
              className="hidden"
              onChange={handleFileChange}
            />
            <label
              htmlFor="fileInput"
              className="cursor-pointer px-6 py-3 bg-gray-800 rounded-xl hover:bg-gray-700 transition-colors w-full text-center"
            >
              Escolher Arquivo
            </label>
            {selectedFile && (
              <p className="text-gray-300 text-sm mt-2">
                Arquivo selecionado: {selectedFile.name}
              </p>
            )}
          </div>
        </div>

        {/* Input de Texto */}
        <div className="p-[3px] rounded-xl bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 animate-gradient">
          <textarea
            id="textInput"
            placeholder="Cole o texto do e-mail aqui..."
            className="w-full h-64 p-6 bg-gray-900 text-gray-200 rounded-xl resize-none focus:outline-none placeholder-gray-400 text-lg"
          />
        </div>

        {/* Botão Analisar */}
        <div className="w-full flex justify-end">
          <button
            onClick={submitText}
            disabled={loading}
            className="px-8 py-4 rounded-xl font-semibold text-white text-lg bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 animate-gradient hover:opacity-90 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading && (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            )}
            {loading ? "Analisando..." : "Analisar"}
          </button>
        </div>

        {/* Resultado */}
        <div className="w-full">
          <h2 className="text-2xl font-bold mb-4 text-center">
            Sugestão de Email:
          </h2>
          <div className="p-6 bg-gray-900 text-gray-200 rounded-xl min-h-[150px] max-h-72 overflow-y-auto transition-opacity duration-300">
            {error && <p className="text-red-500 text-center">{error}</p>}
            {loading && !error && (
              <p className="text-center text-lg">Analisando...</p>
            )}
            {!loading && sugestionEmail && (
              <div className="opacity-100">
                <h3 className="text-lg font-semibold mb-2">
                  {sugestionEmail.label}{" "}
                  {sugestionEmail.score !== undefined && (
                    <> (Confiança: {(sugestionEmail.score * 100).toFixed(2)}%)</>
                  )}
                </h3>
                <p className="text-lg whitespace-pre-wrap">
                  {sugestionEmail.suggested}
                </p>
              </div>
            )}
            {!loading && !sugestionEmail && !error && (
              <p className="text-center text-gray-500">
                Nenhum resultado disponível ainda.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 px-6 py-4 rounded-lg shadow-lg text-white font-semibold animate-slide-in ${
            toast.type === "success" ? "bg-green-500" : "bg-red-500"
          }`}
        >
          {toast.message}
        </div>
      )}

      {/* Animations */}
      <style jsx>{`
        .animate-slide-in {
          animation: slideIn 0.4s ease-out;
        }
        @keyframes slideIn {
          0% {
            opacity: 0;
            transform: translateY(50px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}