"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { databaseAPI, dataAPI } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { ArrowLeft, Plus, Send, Table as TableIcon, Sparkles, Wand2 } from "lucide-react";

export default function DatabasePage() {
  const router = useRouter();
  const params = useParams();
  const dbId = params.id as string;

  const [database, setDatabase] = useState<any>(null);
  const [data, setData] = useState<any[]>([]);
  const [formData, setFormData] = useState<any>({});
  const [nlCommand, setNlCommand] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<"table" | "form" | "command">("table");
  const [chatMessages, setChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string, sql?: string, data?: any[]}>>([]);

  // Helper function to format field names
  const formatFieldName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Auto-fill category using AI
  const handleAICategory = async (fieldName: string) => {
    const itemName = formData['name'] || formData['item'] || formData['item_name'];
    if (!itemName) {
      alert('Please enter an item name first');
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ai/categorize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          item_name: itemName,
          available_categories: []
        })
      });

      const data = await response.json();
      setFormData({ ...formData, [fieldName]: data.category });
    } catch (error) {
      console.error('Failed to get AI suggestion:', error);
    }
  };

  // Auto-fill expiration date using AI
  const handleAIExpiration = async (fieldName: string) => {
    const itemName = formData['name'] || formData['item'] || formData['item_name'];
    const itemType = formData['food_type'] || formData['type'] || formData['category'];

    if (!itemName) {
      alert('Please enter an item name first');
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ai/suggest-expiration`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          item_name: itemName,
          item_type: itemType || null
        })
      });

      const data = await response.json();
      setFormData({ ...formData, [fieldName]: data.expiration_date });
    } catch (error) {
      console.error('Failed to get AI suggestion:', error);
    }
  };

  // Auto-fill description using AI
  const handleAIDescription = async (fieldName: string) => {
    const itemName = formData['name'] || formData['item'] || formData['item_name'];
    if (!itemName) {
      alert('Please enter an item name first');
      return;
    }

    try {
      // Generate a simple description based on available fields
      const otherFields = Object.entries(formData)
        .filter(([key, value]) => value && key !== 'name' && key !== 'item' && key !== 'item_name' && key !== fieldName)
        .map(([key, value]) => `${formatFieldName(key)}: ${value}`)
        .join(', ');

      const description = otherFields
        ? `${itemName} - ${otherFields}`
        : `${itemName}`;

      setFormData({ ...formData, [fieldName]: description });
    } catch (error) {
      console.error('Failed to generate description:', error);
    }
  };

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    loadDatabase();
    loadData();
  }, [dbId]);

  const loadDatabase = async () => {
    try {
      const response = await databaseAPI.get(dbId);
      setDatabase(response.data);
    } catch (error) {
      console.error("Failed to load database:", error);
    }
  };

  const loadData = async () => {
    try {
      const response = await dataAPI.getAll(dbId);
      setData(response.data.data);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await dataAPI.insert(dbId, formData);
      setFormData({});
      await loadData();
      setActiveTab("table");
    } catch (error) {
      console.error("Failed to insert data:", error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNaturalCommand = async () => {
    if (!nlCommand.trim()) return;

    const userMessage = nlCommand.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setNlCommand("");
    setSubmitting(true);

    try {
      const response = await dataAPI.executeNatural(dbId, userMessage);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.explanation || 'Command executed successfully!',
        sql: response.data.sql,
        data: response.data.data
      }]);
      await loadData();
    } catch (error: any) {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: error.response?.data?.detail || "Sorry, I couldn't understand that command. Try rephrasing it."
      }]);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading database...</p>
        </div>
      </div>
    );
  }

  if (!database) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <p className="text-muted-foreground">Database not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 pt-32 pb-16">
      {/* Background Effect */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" />
      </div>

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard")}
            className="mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <h1 className="font-display text-5xl font-bold mb-4">
            {database.display_name}
          </h1>
          <p className="text-xl text-muted-foreground">
            {data.length} {data.length === 1 ? "record" : "records"} • {database.schema.fields?.length} fields
          </p>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={activeTab === "table" ? "default" : "outline"}
            onClick={() => setActiveTab("table")}
          >
            <TableIcon className="w-4 h-4 mr-2" />
            View Data
          </Button>
          <Button
            variant={activeTab === "form" ? "default" : "outline"}
            onClick={() => setActiveTab("form")}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Data
          </Button>
          <Button
            variant={activeTab === "command" ? "default" : "outline"}
            onClick={() => setActiveTab("command")}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            AI Query
          </Button>
        </div>

        {/* Content Area */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Table View */}
          {activeTab === "table" && (
            <Card className="glass-card">
              <CardContent className="p-6">
                {data.length === 0 ? (
                  <div className="text-center py-16">
                    <TableIcon className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-xl text-muted-foreground mb-4">
                      No data yet
                    </p>
                    <Button onClick={() => setActiveTab("form")}>
                      Add Your First Record
                    </Button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          {database.schema.fields?.map((field: any) => (
                            <th
                              key={field.name}
                              className="text-left py-3 px-4 font-semibold text-sm"
                            >
                              {formatFieldName(field.name)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {data.map((row, index) => (
                          <tr
                            key={row.id || index}
                            className="border-b border-gray-100 hover:bg-white/50 transition-colors"
                          >
                            {database.schema.fields?.map((field: any) => (
                              <td key={field.name} className="py-3 px-4 text-sm">
                                {row[field.name] || "-"}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Form View */}
          {activeTab === "form" && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Add New Record</CardTitle>
                <CardDescription>
                  Fill in the fields below to add a new entry
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleFormSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    {database.schema.fields?.map((field: any) => (
                      <div key={field.name} className="space-y-2">
                        <Label htmlFor={field.name}>
                          {formatFieldName(field.name)}
                          {!field.optional && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <div className="flex gap-2">
                          <Input
                            id={field.name}
                            type={
                              field.type === "INTEGER" || field.type === "REAL"
                                ? "number"
                                : field.name.toLowerCase().includes("date") || field.name.toLowerCase().includes("expiration")
                                ? "date"
                                : "text"
                            }
                            step={field.type === "REAL" ? "0.01" : undefined}
                            value={formData[field.name] || ""}
                            onChange={(e) =>
                              setFormData({ ...formData, [field.name]: e.target.value })
                            }
                            required={!field.optional}
                            disabled={submitting}
                            className="flex-1"
                          />
                          {(field.name.toLowerCase().includes("category") ||
                            field.name.toLowerCase().includes("type")) && (
                            <Button
                              type="button"
                              variant="outline"
                              size="icon"
                              onClick={() => handleAICategory(field.name)}
                              disabled={submitting}
                              title="AI suggest category"
                            >
                              <Wand2 className="w-4 h-4" />
                            </Button>
                          )}
                          {field.name.toLowerCase().includes("expiration") && (
                            <Button
                              type="button"
                              variant="outline"
                              size="icon"
                              onClick={() => handleAIExpiration(field.name)}
                              disabled={submitting}
                              title="AI suggest expiration date"
                            >
                              <Wand2 className="w-4 h-4" />
                            </Button>
                          )}
                          {field.name.toLowerCase().includes("description") && (
                            <Button
                              type="button"
                              variant="outline"
                              size="icon"
                              onClick={() => handleAIDescription(field.name)}
                              disabled={submitting}
                              title="AI generate description"
                            >
                              <Wand2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <Button
                    type="submit"
                    size="lg"
                    disabled={submitting}
                    className="w-full"
                  >
                    {submitting ? "Adding..." : "Add Record"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {/* AI Chat */}
          {activeTab === "command" && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  AI Assistant
                </CardTitle>
                <CardDescription>
                  Chat with AI to query or modify your data using natural language
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Chat Messages */}
                <div className="h-[400px] overflow-y-auto border rounded-2xl p-4 bg-gray-50/50 space-y-4">
                  {chatMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
                      <Sparkles className="w-12 h-12 mb-4 opacity-30" />
                      <p className="text-lg font-medium mb-2">Start a conversation</p>
                      <p className="text-sm">Ask me anything about your data!</p>
                    </div>
                  ) : (
                    chatMessages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[85%] p-3 rounded-2xl ${
                            msg.role === 'user'
                              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                              : 'bg-white border border-gray-200 shadow-sm'
                          }`}
                        >
                          <p className="text-sm">{msg.content}</p>
                          {msg.data && msg.data.length > 0 && (
                            <div className="mt-3 overflow-x-auto">
                              <table className="w-full text-xs border-collapse">
                                <thead>
                                  <tr className="bg-gray-100">
                                    {Object.keys(msg.data[0]).filter(k => k !== 'id' && k !== 'created_at').map(key => (
                                      <th key={key} className="p-2 text-left border border-gray-200 font-semibold">
                                        {formatFieldName(key)}
                                      </th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {msg.data.slice(0, 10).map((row, i) => (
                                    <tr key={i} className="hover:bg-gray-50">
                                      {Object.entries(row).filter(([k]) => k !== 'id' && k !== 'created_at').map(([key, value]) => (
                                        <td key={key} className="p-2 border border-gray-200">
                                          {String(value) || '-'}
                                        </td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                              {msg.data.length > 10 && (
                                <p className="text-xs text-gray-500 mt-2">Showing 10 of {msg.data.length} records</p>
                              )}
                            </div>
                          )}
                          {msg.data && msg.data.length === 0 && (
                            <p className="text-xs mt-2 text-gray-500 italic">No records found</p>
                          )}
                          {msg.sql && (
                            <details className="mt-2">
                              <summary className="text-xs cursor-pointer text-gray-500 hover:text-gray-700">View SQL</summary>
                              <p className="text-xs mt-1 font-mono bg-gray-100 p-2 rounded">
                                {msg.sql}
                              </p>
                            </details>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                  {submitting && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-gray-200 shadow-sm p-3 rounded-2xl">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Quick Actions */}
                {chatMessages.length === 0 && (
                  <div className="flex flex-wrap gap-2">
                    {exampleCommands.map((cmd, index) => (
                      <button
                        key={index}
                        onClick={() => setNlCommand(cmd)}
                        className="px-3 py-1.5 rounded-full bg-white border border-gray-200 text-sm hover:bg-purple-50 hover:border-purple-300 transition-all"
                        disabled={submitting}
                      >
                        {cmd}
                      </button>
                    ))}
                  </div>
                )}

                {/* Input */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask anything about your data..."
                    value={nlCommand}
                    onChange={(e) => setNlCommand(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleNaturalCommand()}
                    disabled={submitting}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleNaturalCommand}
                    disabled={submitting || !nlCommand.trim()}
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  );
}

const exampleCommands = [
  "Show me all records",
  "Add a new item",
  "Show me items from the last week",
  "Count how many records I have",
];
