"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { databaseAPI, aiAPI } from "@/lib/api";
import { Sparkles, Check, ArrowLeft, Plus, X, Edit2 } from "lucide-react";

export default function CreateDatabaseWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [description, setDescription] = useState("");
  const [generatedSchema, setGeneratedSchema] = useState<any>(null);
  const [editedSchema, setEditedSchema] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAddField, setShowAddField] = useState(false);
  const [newField, setNewField] = useState({ name: "", type: "TEXT", optional: false });

  const handleGenerateSchema = async () => {
    if (!description.trim()) {
      setError("Please describe what you want to track");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await aiAPI.generateSchema(description);
      const schema = response.data.schema;
      setGeneratedSchema(schema);

      // Initialize edited schema with all fields enabled
      setEditedSchema({
        ...schema,
        fields: schema.fields.map((field: any) => ({ ...field, enabled: true }))
      });

      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate schema");
    } finally {
      setLoading(false);
    }
  };

  const toggleField = (index: number) => {
    const newFields = [...editedSchema.fields];
    newFields[index].enabled = !newFields[index].enabled;
    setEditedSchema({ ...editedSchema, fields: newFields });
  };

  const removeField = (index: number) => {
    const newFields = editedSchema.fields.filter((_: any, i: number) => i !== index);
    setEditedSchema({ ...editedSchema, fields: newFields });
  };

  const addNewField = () => {
    if (!newField.name.trim()) {
      setError("Field name is required");
      return;
    }

    const newFields = [...editedSchema.fields, { ...newField, enabled: true }];
    setEditedSchema({ ...editedSchema, fields: newFields });
    setNewField({ name: "", type: "TEXT", optional: false });
    setShowAddField(false);
    setError("");
  };

  const updateFieldName = (index: number, name: string) => {
    const newFields = [...editedSchema.fields];
    newFields[index].name = name;
    setEditedSchema({ ...editedSchema, fields: newFields });
  };

  const updateFieldType = (index: number, type: string) => {
    const newFields = [...editedSchema.fields];
    newFields[index].type = type;
    setEditedSchema({ ...editedSchema, fields: newFields });
  };

  const toggleFieldOptional = (index: number) => {
    const newFields = [...editedSchema.fields];
    newFields[index].optional = !newFields[index].optional;
    setEditedSchema({ ...editedSchema, fields: newFields });
  };

  const handleConfirm = async () => {
    setLoading(true);
    setError("");

    try {
      await databaseAPI.createWithSchema(editedSchema);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create database");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-4 sm:px-6 pt-24 sm:pt-32 pb-12 sm:pb-16">
      {/* Background Effect */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" />
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 sm:mb-12"
        >
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard")}
            className="mb-4 sm:mb-6 text-sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <h1 className="font-display text-3xl sm:text-5xl font-bold mb-2 sm:mb-4">
            Create New Database
          </h1>
          <p className="text-base sm:text-xl text-muted-foreground">
            Describe what you want to track
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 sm:gap-4 mb-8 sm:mb-12">
          {[1, 2].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-8 sm:w-10 h-8 sm:h-10 rounded-full flex items-center justify-center font-semibold text-sm sm:text-base transition-all ${
                  s === step
                    ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-glow"
                    : s < step
                    ? "bg-green-500 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-400"
                }`}
              >
                {s < step ? <Check className="w-5 h-5" /> : s}
              </div>
              {s < 2 && (
                <div className={`w-8 sm:w-16 h-1 ${s < step ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"}`} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Describe Database */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <Card className="glass-card">
                <CardHeader className="p-4 sm:p-6">
                  <CardTitle className="text-xl sm:text-3xl">
                    What do you want to track?
                  </CardTitle>
                  <CardDescription className="text-sm sm:text-base">
                    Describe your database in plain English. Our AI will create the perfect schema.
                  </CardDescription>
                </CardHeader>

                <CardContent className="p-4 sm:p-6 pt-0 space-y-4 sm:space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="description" className="text-base sm:text-lg">
                      Description
                    </Label>
                    <textarea
                      id="description"
                      className="flex min-h-[150px] sm:min-h-[200px] w-full rounded-xl sm:rounded-2xl border border-input bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm px-3 sm:px-4 py-2 sm:py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                      placeholder="Example: I want to track grocery items with the item name, date bought, store, food type, and expiration date."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      disabled={loading}
                    />
                  </div>

                  {/* Example Prompts */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">
                      Need inspiration? Try these:
                    </p>
                    <div className="grid gap-2">
                      {examplePrompts.map((prompt, index) => (
                        <button
                          key={index}
                          onClick={() => setDescription(prompt)}
                          className="text-left p-2 sm:p-3 rounded-xl sm:rounded-2xl bg-white/50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-xs sm:text-sm transition-all hover:shadow-soft"
                          disabled={loading}
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>

                  {error && (
                    <div className="p-3 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300 text-sm">
                      {error}
                    </div>
                  )}

                  <Button
                    size="lg"
                    onClick={handleGenerateSchema}
                    disabled={loading}
                    className="w-full group"
                  >
                    {loading ? (
                      "Generating schema..."
                    ) : (
                      <>
                        Generate Database
                        <Sparkles className="ml-2 w-4 h-4 group-hover:rotate-12 transition-transform" />
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Step 2: Review & Edit Schema */}
          {step === 2 && editedSchema && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <Card className="glass-card">
                <CardHeader className="p-4 sm:p-6">
                  <CardTitle className="text-xl sm:text-3xl">
                    Customize Your Database
                  </CardTitle>
                  <CardDescription className="text-sm sm:text-base">
                    Review AI suggestions and customize fields as needed
                  </CardDescription>
                </CardHeader>

                <CardContent className="p-4 sm:p-6 pt-0 space-y-4 sm:space-y-6">
                  <div className="p-4 sm:p-6 rounded-xl sm:rounded-2xl bg-gradient-purple dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800">
                    <h3 className="font-display text-lg sm:text-2xl font-semibold mb-1 text-purple-900 dark:text-purple-100">
                      {editedSchema.display_name}
                    </h3>
                    <p className="text-xs sm:text-sm text-purple-700 dark:text-purple-300">
                      Table: {editedSchema.database_name}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-base sm:text-lg">Fields</h4>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAddField(true)}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add Field
                      </Button>
                    </div>

                    {/* Add New Field Form */}
                    {showAddField && (
                      <div className="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 space-y-3">
                        <div className="flex items-center justify-between">
                          <h5 className="font-medium text-sm">Add New Field</h5>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setShowAddField(false);
                              setNewField({ name: "", type: "TEXT", optional: false });
                              setError("");
                            }}
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
                          <Input
                            placeholder="Field name"
                            value={newField.name}
                            onChange={(e) => setNewField({ ...newField, name: e.target.value })}
                          />
                          <select
                            className="flex h-10 w-full rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-2 text-sm"
                            value={newField.type}
                            onChange={(e) => setNewField({ ...newField, type: e.target.value })}
                          >
                            <option value="TEXT">Text</option>
                            <option value="INTEGER">Number (Whole)</option>
                            <option value="REAL">Number (Decimal)</option>
                            <option value="DATE">Date</option>
                          </select>
                          <label className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              checked={newField.optional}
                              onChange={(e) => setNewField({ ...newField, optional: e.target.checked })}
                            />
                            Optional
                          </label>
                        </div>
                        <Button size="sm" onClick={addNewField} className="w-full">
                          Add Field
                        </Button>
                      </div>
                    )}

                    <div className="grid gap-2 sm:gap-3">
                      {editedSchema.fields?.map((field: any, index: number) => (
                        <div
                          key={index}
                          className={`p-3 sm:p-4 rounded-xl sm:rounded-2xl border transition-all ${
                            field.enabled
                              ? "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                              : "bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 opacity-60"
                          }`}
                        >
                          <div className="flex items-start gap-2 sm:gap-3">
                            {/* Checkbox to enable/disable */}
                            <input
                              type="checkbox"
                              checked={field.enabled}
                              onChange={() => toggleField(index)}
                              className="mt-1.5 w-4 h-4 cursor-pointer"
                            />

                            <div className="flex-1 space-y-2">
                              {/* Field Name */}
                              <Input
                                value={field.name}
                                onChange={(e) => updateFieldName(index, e.target.value)}
                                disabled={!field.enabled}
                                className="font-medium"
                              />

                              {/* Field Type and Optional */}
                              <div className="flex flex-wrap gap-2 sm:gap-3 items-center">
                                <select
                                  className="flex h-9 w-full sm:w-40 rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-1 text-sm disabled:opacity-50"
                                  value={field.type}
                                  onChange={(e) => updateFieldType(index, e.target.value)}
                                  disabled={!field.enabled}
                                >
                                  <option value="TEXT">Text</option>
                                  <option value="INTEGER">Number (Whole)</option>
                                  <option value="REAL">Number (Decimal)</option>
                                  <option value="DATE">Date</option>
                                </select>
                                <label className="flex items-center gap-2 text-sm">
                                  <input
                                    type="checkbox"
                                    checked={field.optional}
                                    onChange={() => toggleFieldOptional(index)}
                                    disabled={!field.enabled}
                                  />
                                  Optional
                                </label>
                              </div>
                            </div>

                            {/* Remove button */}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeField(index)}
                              className="mt-1"
                            >
                              <X className="w-4 h-4 text-red-500" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>

                    {editedSchema.fields?.filter((f: any) => f.enabled).length === 0 && (
                      <div className="p-4 rounded-2xl bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200 text-sm">
                        ⚠️ You must enable at least one field to create the database
                      </div>
                    )}
                  </div>

                  {error && (
                    <div className="p-3 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300 text-sm">
                      {error}
                    </div>
                  )}

                  <div className="flex gap-4">
                    <Button
                      variant="outline"
                      onClick={() => setStep(1)}
                      className="flex-1"
                    >
                      Start Over
                    </Button>
                    <Button
                      size="lg"
                      onClick={handleConfirm}
                      disabled={editedSchema.fields?.filter((f: any) => f.enabled).length === 0 || loading}
                      className="flex-1 group"
                    >
                      {loading ? "Creating..." : "Create Database"}
                      {!loading && <Check className="ml-2 w-4 h-4" />}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

const examplePrompts = [
  "I want to track grocery items with name, date bought, store, food type, and expiration date.",
  "Create a workout log with exercise name, sets, reps, weight, and date.",
  "Track my expenses with description, amount, category, date, and payment method.",
  "Manage my book collection with title, author, genre, pages, and reading status.",
];
