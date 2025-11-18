"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { databaseAPI } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Plus, Database, Calendar, ChevronRight } from "lucide-react";

interface DatabaseInfo {
  id: string;
  db_name: string;
  display_name: string;
  schema: any;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [databases, setDatabases] = useState<DatabaseInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    try {
      const response = await databaseAPI.list();
      setDatabases(response.data);
    } catch (error) {
      console.error("Failed to load databases:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your databases...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 pt-32 pb-16">
      {/* Background Effect */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" style={{ animationDelay: "2s" }} />
      </div>

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="font-display text-5xl font-bold mb-4">My Databases</h1>
          <p className="text-xl text-muted-foreground">
            Manage and access all your AI-powered databases
          </p>
        </motion.div>

        {/* Create New Database Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Link href="/wizard/create">
            <Card className="glass-card card-3d border-2 border-dashed border-primary/30 hover:border-primary/60 cursor-pointer group">
              <CardContent className="flex items-center justify-center py-16">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-4 shadow-glow group-hover:scale-110 transition-transform">
                    <Plus className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="font-display text-2xl font-semibold mb-2">
                    Create New Database
                  </h3>
                  <p className="text-muted-foreground">
                    Use natural language to build your custom database
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Database Grid */}
        {databases.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <Database className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
            <p className="text-xl text-muted-foreground">
              No databases yet. Create your first one to get started!
            </p>
          </motion.div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {databases.map((db, index) => (
              <motion.div
                key={db.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.2 }}
              >
                <Link href={`/database/${db.id}`}>
                  <Card className="glass-card card-3d h-full group cursor-pointer">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow">
                          <Database className="w-6 h-6 text-white" />
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                      </div>

                      <CardTitle className="group-hover:text-primary transition-colors">
                        {db.display_name}
                      </CardTitle>

                      <CardDescription className="text-sm">
                        {db.schema.fields?.length || 0} fields
                      </CardDescription>

                      <div className="flex items-center gap-2 text-xs text-muted-foreground pt-4">
                        <Calendar className="w-4 h-4" />
                        Created {formatDate(db.created_at)}
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
