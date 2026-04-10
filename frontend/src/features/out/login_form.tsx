"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Loader2, Lock } from "lucide-react";

export function LoginForm() {
    const [loading, setLoading] = React.useState(false);
    const router = useRouter();

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setLoading(true);

        const formData = new FormData(event.currentTarget);
        const username = formData.get("username");
        const password = formData.get("password");

        try {
            // O FastAPI espera os dados em formato x-www-form-urlencoded por padrão no OAuth2
            const details: Record<string, string> = {
                username: username as string,
                password: password as string,
                grant_type: "password",
            };

            const formBody = Object.keys(details)
                .map((key) => encodeURIComponent(key) + "=" + encodeURIComponent(details[key]))
                .join("&");

                // Caminho localhost - Tela Login
            const response = await fetch("https://localhost:8000/api/v1/auth.py", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formBody,
            });

            if (!response.ok) throw new Error("Usuário ou senha inválidos");

            const data = await response.json();

            // Salva o token (em prod, use cookies HttpOnly para mais segurança)
            localStorage.setItem("auth_token", data.access_token);

            toast.success("Login realizado com sucesso!");
            router.push("/simulation"); // Redireciona para a calculadora
        } catch (error: any) {
            toast.error(error.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex min-h-[80vh] items-center justify-center px-4">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1">
                    <div className="flex justify-center mb-4">
                        <div className="rounded-full bg-primary/10 p-3">
                            <Lock className="h-6 w-6 text-primary" />
                        </div>
                    </div>
                    <CardTitle className="text-2xl text-center">Login</CardTitle>
                    <CardDescription className="text-center">
                        Entre com suas credenciais para acessar a calculadora
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Usuário</Label>
                            <Input id="username" name="username" placeholder="Seu usuário" required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Senha</Label>
                            <Input id="password" name="password" type="password" required />
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Entrar
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}