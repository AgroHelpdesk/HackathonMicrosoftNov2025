import React from "react";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../../authConfig";
import { Button } from "@mui/material";
import { Login } from "@mui/icons-material";
import { gradients, borderRadius, shadows, typography } from "../../theme/designSystem";

export const SignInButton = () => {
    const { instance } = useMsal();

    const handleLogin = (loginType) => {
        if (loginType === "popup") {
            instance.loginPopup(loginRequest).catch(e => {
                console.log(e);
            });
        } else if (loginType === "redirect") {
            instance.loginRedirect(loginRequest).catch(e => {
                console.log(e);
            });
        }
    };

    return (
        <Button
            variant="contained"
            startIcon={<Login />}
            onClick={() => handleLogin("popup")}
            sx={{
                background: gradients.primary,
                borderRadius: borderRadius.base,
                fontWeight: typography.fontWeight.medium,
                boxShadow: shadows.button,
                '&:hover': {
                    background: gradients.primary,
                    boxShadow: shadows.md
                }
            }}
        >
            Sign In
        </Button>
    );
}
